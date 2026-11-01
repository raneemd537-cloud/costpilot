const { spawn } = require('node:child_process');
const http = require('node:http');
const os = require('node:os');
const path = require('node:path');
const fs = require('node:fs');
const assert = require('node:assert/strict');

const PORT = 8769;
const SERVER_URL = `http://127.0.0.1:${PORT}`;
const PYTHON_PATH = 'C:\\Users\\khatib\\anaconda3\\python.exe';
const CHROME_PATH = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const WORK_DIR = path.resolve(__dirname, '..');
const TEST_DATA_DIR = path.join(WORK_DIR, 'test_e2e_data');

class CdpClient {
  constructor(wsUrl) {
    this.wsUrl = wsUrl;
    this.id = 1;
    this.callbacks = new Map();
    this.events = [];
    this.consoleErrors = [];
    this.pageErrors = [];
  }

  async connect() {
    this.ws = new WebSocket(this.wsUrl);
    await new Promise((resolve, reject) => {
      this.ws.onopen = resolve;
      this.ws.onerror = reject;
    });

    this.ws.onmessage = event => {
      const msg = JSON.parse(event.data);
      if (msg.id && this.callbacks.has(msg.id)) {
        const { resolve, reject } = this.callbacks.get(msg.id);
        this.callbacks.delete(msg.id);
        if (msg.error) reject(new Error(msg.error.message));
        else resolve(msg.result);
      } else if (msg.method) {
        this.events.push(msg);
        if (msg.method === 'Runtime.consoleAPICalled') {
          if (msg.params.type === 'error') {
            this.consoleErrors.push(msg.params.args.map(a => a.value || a.description).join(' '));
          }
        } else if (msg.method === 'Runtime.exceptionThrown') {
          this.pageErrors.push(msg.params.exceptionDetails.text + ' ' + (msg.params.exceptionDetails.exception?.description || ''));
        }
      }
    };

    await this.send('Page.enable');
    await this.send('Runtime.enable');
    await this.send('DOM.enable');
  }

  send(method, params = {}) {
    return new Promise((resolve, reject) => {
      const id = this.id++;
      this.callbacks.set(id, { resolve, reject });
      this.ws.send(JSON.stringify({ id, method, params }));
    });
  }

  async eval(expression) {
    const res = await this.send('Runtime.evaluate', {
      expression,
      returnByValue: true,
      awaitPromise: true,
    });
    if (res.exceptionDetails) {
      throw new Error('Eval error: ' + (res.exceptionDetails.exception?.description || res.exceptionDetails.text));
    }
    return res.result?.value;
  }

  async navigate(url) {
    await this.send('Page.navigate', { url });
    for (let i = 0; i < 40; i++) {
      await new Promise(resolve => setTimeout(resolve, 200));
      const ready = await this.eval('document.readyState').catch(() => null);
      const title = await this.eval('document.title').catch(() => null);
      if (ready === 'complete' && title) break;
    }
  }

  close() {
    if (this.ws) this.ws.close();
  }
}

async function run() {
  console.log('--- STARTING COMPREHENSIVE E2E BROWSER AUDIT ---');
  if (fs.existsSync(TEST_DATA_DIR)) fs.rmSync(TEST_DATA_DIR, { recursive: true, force: true });

  // 1. Start backend server
  console.log('1. Starting test backend server on port', PORT);
  const serverProc = spawn(PYTHON_PATH, ['-m', 'app.server'], {
    cwd: WORK_DIR,
    env: {
      ...process.env,
      DECISION_LAB_PORT: String(PORT),
      DECISION_LAB_DATA: TEST_DATA_DIR,
    },
    stdio: 'pipe',
  });

  serverProc.stderr.on('data', d => {
    // python prints server logs to stderr
  });

  // Wait for server to be responsive
  let serverReady = false;
  for (let i = 0; i < 30; i++) {
    try {
      const res = await fetch(`${SERVER_URL}/api/session`);
      if (res.ok) { serverReady = true; break; }
    } catch {}
    await new Promise(r => setTimeout(r, 200));
  }
  assert.ok(serverReady, 'Backend server must be ready and responding');
  console.log('   Backend server is UP.');

  // 2. Start Headless Chrome
  console.log('2. Starting Headless Chrome...');
  const tmpProfile = path.join(os.tmpdir(), 'cp-e2e-chrome-' + Date.now());
  const chromeProc = spawn(CHROME_PATH, [
    '--headless=new',
    '--remote-debugging-port=9223',
    '--no-first-run',
    '--no-default-browser-check',
    `--user-data-dir=${tmpProfile}`,
  ]);

  let chromeWsUrl = null;
  for (let i = 0; i < 30; i++) {
    try {
      const res = await fetch('http://127.0.0.1:9223/json/list');
      const tabs = await res.json();
      if (tabs.length && tabs[0].webSocketDebuggerUrl) {
        chromeWsUrl = tabs[0].webSocketDebuggerUrl;
        break;
      }
    } catch {}
    await new Promise(r => setTimeout(r, 200));
  }
  assert.ok(chromeWsUrl, 'Chrome WebSocket URL must be available');
  console.log('   Chrome CDP is ready at', chromeWsUrl);

  const cdp = new CdpClient(chromeWsUrl);
  await cdp.connect();

  try {
    // 3. Test Initial Page Load & Assets
    console.log('3. Navigating to', SERVER_URL);
    await cdp.navigate(SERVER_URL);

    const title = await cdp.eval('document.title');
    assert.equal(title, 'CostPilot — Product Cost & Profit Lab');
    console.log('   ✓ Page title verified:', title);

    const initialLang = await cdp.eval('document.documentElement.lang');
    const initialDir = await cdp.eval('document.documentElement.dir');
    assert.equal(initialLang, 'en');
    assert.equal(initialDir, 'ltr');
    console.log('   ✓ Initial LTR / English layout verified');

    // Verify empty state hero
    const hasEmptyHero = await cdp.eval('!!document.querySelector(".empty-hero")');
    assert.ok(hasEmptyHero, 'Empty state hero should be rendered when no products exist');
    console.log('   ✓ Empty state dashboard rendered properly');

    // 4. Test Navigation Across All Routes
    console.log('4. Testing Tab & View Navigation...');
    const routes = ['products', 'calculator', 'history', 'settings', 'dashboard'];
    for (const route of routes) {
      await cdp.eval(`navigate('${route}')`);
      const currentRoute = await cdp.eval('state.route');
      assert.equal(currentRoute, route);
      const activeNav = await cdp.eval(`document.querySelector('.nav-item.active')?.dataset.route`);
      assert.equal(activeNav, route);
    }
    console.log('   ✓ All 5 primary routes navigated and synchronized with nav state');

    // 5. Test Quick Calculator Form & Financial Math Independently
    console.log('5. Testing Quick Calculator financial formulas & rendering...');
    await cdp.eval(`navigate('calculator')`);
    await cdp.eval(`
      const f = document.querySelector('#quickCalcForm');
      f.elements.name.value = 'Ceramic Coffee Mug';
      f.elements.currency.value = 'USD';
      f.elements.quantity.value = '100';
      f.elements.unit_cost.value = '12.50';
      f.elements.selling_price.value = '25.00';
      f.elements.discount_percent.value = '10';
      f.elements.target_basis.value = 'margin';
      f.elements.target_profit_percent.value = '30';
    `);

    // Submit calculator
    await cdp.eval(`
      const f = document.querySelector('#quickCalcForm');
      f.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
    `);
    await new Promise(r => setTimeout(r, 600));

    // Read calculator result
    const resultCardExists = await cdp.eval('!!document.querySelector("#quickCalcResult .result-card")');
    assert.ok(resultCardExists, 'Result card must render after quick calculation');

    // Independent mathematical verification:
    // Quantity = 100
    // Unit cost = 12.50 -> Purchase total = 1250.00
    // Selling price = 25.00 with 10% discount -> final unit price = 25.00 * 0.90 = 22.50
    // Revenue = 100 * 22.50 = 2250.00
    // Profit = Revenue - Total Cost = 2250.00 - 1250.00 = 1000.00
    // Margin % = 1000.00 / 2250.00 = 44.4444... -> 44.44%
    // Break-even unit price = 12.50 / (1 - 0.10) = 13.8888... -> 13.89
    // Target 30% margin unit price: cost_unit / ((1 - 0.30) * (1 - 0.10)) = 12.50 / (0.70 * 0.90) = 12.50 / 0.63 = 19.8412... -> 19.85
    const renderedProfit = await cdp.eval('document.querySelector("#quickCalcResult .result-amount").textContent');
    assert.ok(renderedProfit.includes('$1,000.00') || renderedProfit.includes('1,000.00'), `Profit must be $1,000.00, got: ${renderedProfit}`);
    console.log('   ✓ Quick calculation verified independently: profit is exact $1,000.00');

    // 6. Test Multi-Step Product Wizard (Add Product)
    console.log('6. Testing Product Wizard (Add Product)...');
    await cdp.eval(`openWizard()`);
    const wizardOpen = await cdp.eval('document.querySelector("#wizardDialog").open');
    assert.ok(wizardOpen, 'Wizard modal must be open');

    // Step 0: Product Info
    await cdp.eval(`
      const b = document.querySelector('#wizardBody');
      b.querySelector('[name="name"]').value = 'Premium Wool Blanket';
      b.querySelector('[name="category"]').value = 'Home Textiles';
      b.querySelector('[name="currency"]').value = 'USD';
      b.querySelector('[name="unit_cost"]').value = '40.00';
      b.querySelector('[name="quantity"]').value = '50';
      b.querySelector('[name="weight"]').value = '1.8';
      captureStep();
      state.step++;
      renderWizardStep();
    `);

    // Step 1: Expenses
    await cdp.eval(`
      state.draft.expenses = [{ name: 'Custom Ribbons & Boxes', amount: '150.00', allocation: 'direct' }];
      captureStep();
      state.step++;
      renderWizardStep();
    `);

    // Step 2: Pricing
    await cdp.eval(`
      const b = document.querySelector('#wizardBody');
      b.querySelector('[name="selling_price"]').value = '80.00';
      b.querySelector('[name="discount_percent"]').value = '5';
      b.querySelector('[name="target_basis"]').value = 'margin';
      b.querySelector('[name="target_profit_percent"]').value = '25';
      captureStep();
      state.step++;
      renderWizardStep();
    `);

    // Step 3: Review & Submit
    const reviewName = await cdp.eval('document.querySelector(".review-product-head strong")?.textContent');
    assert.equal(reviewName, 'Premium Wool Blanket');
    console.log('   ✓ Wizard review step accurately reflects inputs:', reviewName);

    await cdp.eval(`submitWizard()`);
    await new Promise(r => setTimeout(r, 1200));

    // Confirm product now exists in workspace
    const productCount = await cdp.eval('state.products.length');
    assert.equal(productCount, 1, 'Expected exactly 1 product in state');
    const p1 = await cdp.eval('state.products[0]');
    assert.equal(p1.name, 'Premium Wool Blanket');
    console.log('   ✓ Product created and saved successfully into workspace database');

    // Independent Math Verification on saved product:
    // Quantity = 50, Unit purchase = 40.00 -> purchase total = 2000.00
    // Direct expenses = 150.00 -> Total cost = 2150.00
    // Selling price = 80.00, discount = 5% -> final unit price = 80.00 * 0.95 = 76.00
    // Revenue = 50 * 76.00 = 3800.00
    // Profit = 3800.00 - 2150.00 = 1650.00
    // Margin % = 1650.00 / 3800.00 = 43.42105... -> 43.42%
    // Break-even total = 2150.00 -> break-even unit price before discount = 2150.00 / 50 / 0.95 = 43.00 / 0.95 = 45.26315... -> 45.27
    assert.equal(p1.result.total_cost, '2150.00');
    assert.equal(p1.result.revenue, '3800.00');
    assert.equal(p1.result.profit, '1650.00');
    assert.equal(p1.result.margin_percent, '43.42');
    assert.equal(p1.result.break_even_unit_price, '45.27');
    console.log('   ✓ Financial calculations on saved product verified to the cent: profit $1,650.00, margin 43.42%');

    // 7. Test Product Scenarios
    console.log('7. Testing Pricing Scenarios for product...');
    await cdp.eval(`openProduct('${p1.id}', 'scenarios')`);
    await new Promise(r => setTimeout(r, 600));

    // Add scenario
    await cdp.eval(`
      openScenario(state.products[0]);
      const sf = document.querySelector('#scenarioForm');
      sf.elements.name.value = 'Clearance Sale';
      sf.elements.selling_price.value = '60.00';
      sf.elements.discount_percent.value = '0';
      sf.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
    `);
    await new Promise(r => setTimeout(r, 800));

    // Verify scenario in table
    // For 60.00, discount 0%:
    // Revenue = 50 * 60 = 3000.00
    // Cost = 2150.00
    // Profit = 3000 - 2150 = 850.00
    const scenarioRowText = await cdp.eval('document.querySelector("#scenarioList .scenario-row")?.textContent');
    assert.ok(scenarioRowText.includes('Clearance Sale'));
    assert.ok(scenarioRowText.includes('850.00'));
    console.log('   ✓ Scenario saved and dynamically calculated: profit $850.00');

    await cdp.eval(`document.querySelector('#detailDialog').close()`);

    // 8. Test Shared Expense Allocation
    console.log('8. Testing Shared Expense Allocation across multiple products...');
    // Create second product in USD:
    await cdp.eval(`
      state.editing = null;
      state.draft = {
        name: 'Cotton Hand Towel',
        category: 'Bath',
        currency: 'USD',
        unit_cost: 5.00,
        quantity: 50,
        weight: 0.2,
        selling_price: 15.00,
        discount_percent: 0,
        target_basis: 'margin',
        target_profit_percent: 20,
        expenses: []
      };
      await submitWizard();
    `);
    await new Promise(r => setTimeout(r, 1000));
    const allProducts = await cdp.eval('state.products.length');
    assert.equal(allProducts, 2, 'Should have 2 products');

    // Allocate $200.00 shared packaging by quantity (50 units each -> 50% split = $100.00 each)
    await cdp.eval(`
      const p1 = state.products[0], p2 = state.products[1];
      await api('/api/shared-expenses', {
        method: 'POST',
        body: {
          name: 'Shared Warehouse Inbound',
          amount: '200.00',
          basis: 'quantity',
          product_ids: [p1.id, p2.id]
        }
      });
      await loadWorkspace();
    `);

    const updatedP1 = await cdp.eval('state.products.find(p => p.name === "Premium Wool Blanket")');
    // Previous cost was 2150.00, now + 100.00 shared = 2250.00
    // Previous profit was 1650.00, now - 100.00 shared = 1550.00
    assert.equal(updatedP1.result.total_cost, '2250.00');
    assert.equal(updatedP1.result.profit, '1550.00');
    console.log('   ✓ Shared expense allocated and reconciled: cost 2250.00, profit 1550.00');

    // Also check scenario dynamic recalculation in browser!
    await cdp.eval(`
      const scenarios = await api('/api/products/${updatedP1.id}/scenarios');
      state.testScenarios = scenarios;
    `);
    const dynamicScenario = await cdp.eval('state.testScenarios[0]');
    // Clearance sale was 3000 revenue. Cost is now 2250. Profit must now be 750.00!
    assert.equal(dynamicScenario.result.total_cost, '2250.00');
    assert.equal(dynamicScenario.result.profit, '750.00');
    console.log('   ✓ Scenario dynamically recalculated after shared cost change: profit updated to $750.00');

    // 9. Test Localization & RTL
    console.log('9. Testing Arabic RTL Layout and Translations...');
    await cdp.eval(`
      state.lang = 'ar';
      setLocale();
    `);
    const arLang = await cdp.eval('document.documentElement.lang');
    const arDir = await cdp.eval('document.documentElement.dir');
    assert.equal(arLang, 'ar');
    assert.equal(arDir, 'rtl');

    const arHeading = await cdp.eval('document.querySelector("#pageHeading")?.textContent');
    assert.ok(arHeading.length > 0);
    console.log('   ✓ Arabic language set, dir="rtl", page heading translated:', arHeading);

    // Open shared expense dialog in Arabic:
    await cdp.eval(`openSharedDialog()`);
    const arSharedTitle = await cdp.eval('document.querySelector("#sharedTitle")?.textContent');
    assert.equal(arSharedTitle, 'مصروف مشترك');
    const arAllocateBtn = await cdp.eval('document.querySelector("#sharedForm button[type=\\"submit\\"]")?.textContent');
    assert.equal(arAllocateBtn, 'توزيع المصروف');
    console.log('   ✓ Shared expenses modal fully localized in Arabic');
    await cdp.eval(`document.querySelector("#sharedDialog").close()`);

    // Switch back to English
    await cdp.eval(`
      state.lang = 'en';
      setLocale();
    `);
    assert.equal(await cdp.eval('document.documentElement.dir'), 'ltr');

    // 10. Test Theme Toggle (Dark / Light Mode)
    console.log('10. Testing Dark & Light Theme Toggle...');
    await cdp.eval(`
      state.theme = 'dark';
      setLocale();
    `);
    assert.equal(await cdp.eval('document.body.dataset.theme'), 'dark');
    await cdp.eval(`
      state.theme = 'light';
      setLocale();
    `);
    assert.equal(await cdp.eval('document.body.dataset.theme'), 'light');
    console.log('   ✓ Theme toggles verified: dark and light mode conform cleanly');

    // 11. Test Responsive Viewports (Mobile, Tablet, Desktop)
    console.log('11. Testing Responsive Viewports & Mobile Drawer...');
    // Mobile: 375x667
    await cdp.send('Emulation.setDeviceMetricsOverride', {
      width: 375, height: 667, deviceScaleFactor: 2, mobile: true,
    });
    // Check mobile drawer button
    const mobileBtnVisible = await cdp.eval('window.getComputedStyle(document.querySelector("#mobileMenu")).display !== "none"');
    assert.ok(mobileBtnVisible, 'Mobile menu button should be visible on 375px screens');

    // Click mobile menu to open drawer
    await cdp.eval('document.querySelector("#mobileMenu").click()');
    const drawerOpen = await cdp.eval('document.querySelector("#sidebar").classList.contains("sidebar-open")');
    const ariaExp = await cdp.eval('document.querySelector("#mobileMenu").getAttribute("aria-expanded")');
    assert.ok(drawerOpen, 'Sidebar should open on mobile hamburger click');
    assert.equal(ariaExp, 'true');

    // Click nav link to navigate: should close drawer and update aria-expanded
    await cdp.eval('navigate("calculator")');
    const drawerClosed = await cdp.eval('!document.querySelector("#sidebar").classList.contains("sidebar-open")');
    const ariaExpClosed = await cdp.eval('document.querySelector("#mobileMenu").getAttribute("aria-expanded")');
    assert.ok(drawerClosed, 'Sidebar should close after navigation');
    assert.equal(ariaExpClosed, 'false');
    console.log('   ✓ Mobile responsive drawer & aria-expanded state flow verified');

    // Reset viewport to Desktop (1280x800)
    await cdp.send('Emulation.setDeviceMetricsOverride', {
      width: 1280, height: 800, deviceScaleFactor: 1, mobile: false,
    });

    // 12. Test Extreme Financial Edge Cases
    console.log('12. Testing Extreme Financial Inputs (Zero cost, Zero price, 100% discount, Millions)...');
    // Zero cost:
    const zeroCostRes = await cdp.eval(`
      await api('/api/preview', {
        method: 'POST',
        body: { name: 'Free Stock', currency: 'USD', quantity: 10, unit_cost: 0, selling_price: 50, discount_percent: 0, expenses: [] }
      })
    `);
    assert.equal(zeroCostRes.result.profit, '500.00');
    assert.equal(zeroCostRes.result.margin_percent, '100.00');
    assert.equal(zeroCostRes.result.status, 'profit');
    console.log('   ✓ Zero purchase cost correctly calculates 100% margin ($500.00 profit)');

    // 100% discount:
    const fullDiscountRes = await cdp.eval(`
      await api('/api/preview', {
        method: 'POST',
        body: { name: 'Gift Giveaway', currency: 'USD', quantity: 10, unit_cost: 20, selling_price: 50, discount_percent: 100, expenses: [] }
      })
    `);
    assert.equal(fullDiscountRes.result.revenue, '0.00');
    assert.equal(fullDiscountRes.result.profit, '-200.00');
    assert.equal(fullDiscountRes.result.break_even_unit_price, null);
    assert.equal(fullDiscountRes.result.status, 'loss');
    console.log('   ✓ 100% discount correctly handles zero revenue, -$200 loss, and null break-even');

    // High volume & large money values:
    const largeRes = await cdp.eval(`
      await api('/api/preview', {
        method: 'POST',
        body: { name: 'Industrial Batch', currency: 'USD', quantity: 1000000, unit_cost: 5.50, selling_price: 12.00, discount_percent: 5, expenses: [] }
      })
    `);
    // Selling price after 5% = 11.40
    // Revenue = 1,000,000 * 11.40 = 11,400,000.00
    // Cost = 1,000,000 * 5.50 = 5,500,000.00
    // Profit = 5,900,000.00
    assert.equal(largeRes.result.revenue, '11400000.00');
    assert.equal(largeRes.result.total_cost, '5500000.00');
    assert.equal(largeRes.result.profit, '5900000.00');
    console.log('   ✓ High volume calculation exact: $5,900,000.00 profit without precision loss');

    // 13. Search Input Behavior
    console.log('13. Testing Search Filtering & Auto-Routing...');
    await cdp.eval(`navigate('history')`);
    await cdp.eval(`
      const s = document.querySelector('#searchInput');
      s.value = 'Blanket';
      s.dispatchEvent(new Event('input', { bubbles: true }));
    `);
    const routedTo = await cdp.eval('state.route');
    assert.equal(routedTo, 'products');
    const visibleCards = await cdp.eval('document.querySelectorAll(".product-card:not([hidden])").length');
    assert.equal(visibleCards, 1);
    console.log('   ✓ Typing in search bar auto-navigates to products and filters correctly');

    // 14. Check for Console Errors or Unhandled Exceptions
    console.log('14. Checking Console Errors & Page Exceptions...');
    console.log('   Total console errors captured:', cdp.consoleErrors.length);
    console.log('   Total page exceptions captured:', cdp.pageErrors.length);
    if (cdp.consoleErrors.length > 0) {
      console.warn('   Console error logs:', cdp.consoleErrors);
    }
    if (cdp.pageErrors.length > 0) {
      console.error('   Page exceptions:', cdp.pageErrors);
    }
    assert.equal(cdp.pageErrors.length, 0, 'There must be NO unhandled page exceptions');
    console.log('   ✓ Zero unhandled exceptions in browser runtime');

    console.log('\n========================================');
    console.log('ALL E2E BROWSER TESTS PASSED SUCCESSFULLY!');
    console.log('========================================\n');
  } finally {
    cdp.close();
    chromeProc.kill('SIGKILL');
    serverProc.kill('SIGKILL');
    if (fs.existsSync(TEST_DATA_DIR)) {
      try { fs.rmSync(TEST_DATA_DIR, { recursive: true, force: true }); } catch {}
    }
  }
}

run().catch(err => {
  console.error('\nE2E TEST FAILURE:', err);
  process.exit(1);
});
