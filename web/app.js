const CURRENCIES = ['USD', 'EUR', 'GBP', 'ILS', 'JOD', 'SAR', 'AED', 'EGP'];
const currencySymbols = { USD: '$', EUR: '€', GBP: '£', ILS: '₪', JOD: 'د.أ', SAR: 'ر.س', AED: 'د.إ', EGP: 'ج.م' };
const words = {
  en: {
    workspace:'WORKSPACE', dashboard:'Dashboard', products:'Products', calculator:'Calculator', history:'Activity', settings:'Settings',
    helpTitle:'Make every price count.', helpCopy:'Know your numbers before you sell.', openCalculator:'Open calculator ↗', productWorkspace:'PRODUCT WORKSPACE', addProductTitle:'Add a product',
    voiceTitle:'Tell us about your product', voiceCopy:'Browser speech recognition may send audio to its provider. Review every field before saving.', voiceStart:'Start voice input', voiceStop:'Stop recording', back:'Back', continue:'Continue', saveCalculate:'Calculate & save',
    productDetails:'PRODUCT DETAILS', editProduct:'Edit product', tabInfo:'Product info', tabExpenses:'Expenses', tabProfit:'Profit & loss', tabScenarios:'Scenarios', pricingLab:'PRICING LAB', newScenario:'New scenario',
    scenarioName:'Scenario name', sellingPrice:'Selling price', discount:'Discount', cancel:'Cancel', saveScenario:'Save scenario', editScenario:'Edit scenario', saveChanges:'Save changes', yourWorkspace:'YOUR WORKSPACE', createAccount:'Create your account', email:'Email', password:'Password', passwordHint:'Use at least 12 characters.',
    guestChoice:'What should happen to your guest data?', transferData:'Transfer my products and history', transferExplain:'Move your current workspace into this account.', startFresh:'Start with an empty account', freshExplain:'Keep this guest workspace separate.', haveAccount:'Already have an account? Sign in', signIn:'Sign in', noAccount:'New here? Create an account', googleContinue:'Continue with Google', googleUnavailable:'Google sign-in is not configured on this server yet.', googleFailed:'Google sign-in could not be completed. Please try again.', googleCancelled:'Google sign-in was cancelled.', forgotPassword:'Forgot password?', resetPassword:'Reset password', resetSubtitle:'Enter your email and we will send you a reset link.', sendReset:'Send reset link', resetSent:'If that email is registered, a reset link has been sent.', accountSecurity:'ACCOUNT SECURITY',
    overview:'Here’s your business at a glance.', goodMorning:'Good to see you', addProduct:'+ Add product', allProducts:'All products', recentProducts:'Recent products', viewAll:'View all', totalProducts:'Products tracked', profitThisMonth:'Current total profit', averageMargin:'Avg. margin (profit ÷ revenue)', calculations:'Calculations',
    profit:'Profit', loss:'Loss', breakEven:'Break-even price before discount', break_even:'Break-even', revenue:'Revenue', totalCost:'Total cost', margin:'Profit margin / final selling price', targetPrice:'Target selling price', targetFixed:'Fixed profit target', targetPercent:'Percentage target',
    noProducts:'Your next great decision starts here.', emptyCopy:'Add a product to see its true cost, break-even point, and profit before you sell.', startAdding:'Add your first product', productList:'Your products', productListCopy:'A clear view of what you sell and what you earn.', searchPlaceholder:'Search products...',
    chartTitle:'Profit by currency', chartSubtitle:'Your recorded results, kept in separate currencies.', recentActivity:'Recent calculations', noActivity:'Your calculations will appear here.', quickCalculator:'Quick calculator', quickCopy:'Start with a price. We’ll help you see the full picture.', openLab:'Open pricing lab',
    stepInfo:'Product info', stepExpenses:'Expenses', stepPricing:'Pricing', stepReview:'Review', name:'Product name', category:'Category (optional)', currency:'Currency', unitCost:'Unit purchase cost', quantity:'Quantity purchased', weight:'Product weight (optional)',
    expenseName:'Expense name', amount:'Amount', addExpense:'Add an expense', noExpenses:'No product-specific expenses added.', expenseHelp:'Only expenses paid by the seller belong here. Customer-paid delivery is excluded.', directExpense:'Product-specific expense', expenseLabel:'e.g. Packaging', purchaseDetails:'PURCHASE DETAILS', pricingDetails:'PRICING DETAILS', reviewNote:'Check the details below. Saving will record a calculation for this product.',
    totalPurchase:'Total purchase cost', allocatedExpenses:'Additional expenses', finalPrice:'Final price after discount', targetBasis:'Percentage target means', marginBasis:'Profit ÷ selling price (margin)', markupBasis:'Profit ÷ total cost (markup)',
    allCurrencies:'All currencies', noResults:'No products match that search.', edit:'Edit', delete:'Delete', confirmDelete:'Delete this product and its scenarios? Shared expenses will be recalculated for the remaining products.', saved:'Product saved and calculation recorded.', updated:'Product updated.', deleted:'Product deleted.',
    infoTitle:'Product information', expenseBreakdown:'Cost breakdown', scenarioCompare:'Compare pricing scenarios', addScenario:'Add scenario', noScenarios:'No scenarios yet. Add prices you want to compare.',
    scenario:'Scenario', price:'Original price', discountShort:'Discount', finalUnit:'Final unit price', wholeProfit:'Profit / loss total', needed:'Required price', deleteConfirm:'Delete this scenario?', scenarioSaved:'Scenario saved.', settingsTitle:'Your preferences', language:'Language', appearance:'Appearance', lightMode:'Light mode', darkMode:'Dark mode', accountTitle:'Your account', guestInfo:'You’re using a guest workspace. Your data is saved in this browser’s local app database.', createAccountAction:'Create account', logout:'Sign out',
    activityTitle:'Calculation activity', activityCopy:'A record of calculations you confirmed.', date:'Date', inputSummary:'Inputs', result:'Result', suggestions:'Suggest profit improvements', suggestionsTitle:'Ideas to review', suggestionsLimit:'These are arithmetic comparisons only. They do not predict customer demand or sales volume.', noSuggestions:'No higher comparison price is available for the current price and discount.', suggestionAlreadyHigh:'Your current price is already at or above the comparison price.', suggestionNoBreakEven:'A full discount leaves no finite break-even price to compare.', aiReview:'AI financial review', aiConsent:'This sends this product’s financial inputs and results to OpenAI for review. Continue?', aiDisclaimer:'AI commentary can be wrong. Financial figures above are calculated locally and remain authoritative.', aiUnavailable:'AI review is not configured on this server.',
    required:'Please fill in the required fields.', invalidVoice:'Some values could not be read clearly. Review and enter any missing details yourself.', unsupportedVoice:'Voice recognition is not available in this browser. Try Chrome or Edge.', permissionVoice:'Microphone access was blocked. Allow microphone access in your browser settings and try again.', recording:'Listening… speak naturally, then stop to review.', stoppingVoice:'Finishing speech recognition…', stoppedVoice:'Recording stopped. Review any captured fields.', noSpeechVoice:'No speech was detected. Try again or enter details manually.', networkVoice:'Speech service is unavailable. Check your connection and try again.', microphoneVoice:'No microphone was found. Check the device and try again.', stoppingVoice:'Finishing speech recognition…', stoppedVoice:'Recording stopped. Review any captured fields.', noSpeechVoice:'No speech was detected. Try again or enter details manually.', networkVoice:'Speech service is unavailable. Check your connection and try again.', microphoneVoice:'No microphone was found. Check the device and try again.', transcribed:'Speech transcribed. Check the highlighted fields before continuing.', voiceError:'Voice input stopped. You can enter the details manually.', loading:'Loading…', error:'Something went wrong. Please try again.',
    ltr:'English', rtl:'العربية', settingsSaved:'Preference saved.', targetMeaning:'The target percentage denominator is explicit and can be changed.', noHistory:'No calculations recorded yet.', currencyTotals:'Currency totals', other:'other', cost:'Cost', unit:'unit', fixed:'Fixed', percentage:'Percentage', choose:'Choose…', item:'item', expensesHeading:'Additional expenses', step:'Step', close:'Close', or:'or', sharedExpenseTitle:'Shared expense', sharedExpenseSubtitle:'Choose products in one currency and an allocation basis.', sharedExpenseBasis:'Allocation basis', sharedExpenseNote:'Supplier-to-seller shipping has no special rule yet. Add it only as a general shared expense with an explicit basis. Customer-paid delivery is excluded.', allocateExpense:'Allocate expense', sharedPlaceholder:'Supplier fee, shared packaging…', sharedAction:'Shared expense',
  },
  ar: {
    workspace:'مساحة العمل', dashboard:'لوحة المعلومات', products:'المنتجات', calculator:'الحاسبة', history:'النشاط', settings:'الإعدادات',
    helpTitle:'كل سعر مهم.', helpCopy:'اعرف أرقامك قبل البيع.', openCalculator:'افتح الحاسبة ↗', productWorkspace:'مساحة المنتج', addProductTitle:'أضف منتجاً',
    voiceTitle:'أخبرنا عن منتجك', voiceCopy:'قد يرسل التعرف الصوتي في المتصفح الصوت إلى مزوده. راجع كل حقل قبل الحفظ.', voiceStart:'ابدأ الإدخال الصوتي', voiceStop:'أوقف التسجيل', back:'رجوع', continue:'متابعة', saveCalculate:'احسب واحفظ',
    productDetails:'تفاصيل المنتج', editProduct:'تعديل المنتج', tabInfo:'معلومات المنتج', tabExpenses:'المصاريف', tabProfit:'الربح والخسارة', tabScenarios:'السيناريوهات', pricingLab:'مختبر التسعير', newScenario:'سيناريو جديد',
    scenarioName:'اسم السيناريو', sellingPrice:'سعر البيع', discount:'الخصم', cancel:'إلغاء', saveScenario:'احفظ السيناريو', editScenario:'عدّل السيناريو', saveChanges:'احفظ التعديلات', yourWorkspace:'مساحة عملك', createAccount:'أنشئ حساباً', email:'البريد الإلكتروني', password:'كلمة المرور', passwordHint:'استخدم 12 حرفاً على الأقل.',
    guestChoice:'ماذا تريد أن يحدث لبيانات الضيف؟', transferData:'انقل منتجاتي وسجلي', transferExplain:'انقل مساحة العمل الحالية إلى هذا الحساب.', startFresh:'ابدأ بحساب فارغ', freshExplain:'اترك مساحة الضيف منفصلة.', haveAccount:'لديك حساب؟ تسجيل الدخول', signIn:'تسجيل الدخول', noAccount:'جديد هنا؟ أنشئ حساباً', forgotPassword:'نسيت كلمة المرور؟', resetPassword:'إعادة تعيين كلمة المرور', resetSubtitle:'أدخل بريدك الإلكتروني وسنرسل لك رابطاً لإعادة التعيين.', sendReset:'إرسال رابط التعيين', resetSent:'إذا كان البريد مسجلاً، فقد تم إرسال رابط إعادة التعيين.', accountSecurity:'أمان الحساب',
    overview:'إليك ملخص نشاطك التجاري.', goodMorning:'أهلاً بعودتك', addProduct:'+ أضف منتجاً', allProducts:'كل المنتجات', recentProducts:'أحدث المنتجات', viewAll:'عرض الكل', totalProducts:'المنتجات المسجلة', profitThisMonth:'إجمالي الربح الحالي', averageMargin:'متوسط الهامش (الربح ÷ الإيرادات)', calculations:'الحسابات',
    profit:'ربح', loss:'خسارة', breakEven:'سعر التعادل قبل الخصم', break_even:'نقطة التعادل', revenue:'الإيرادات', totalCost:'التكلفة الإجمالية', margin:'هامش الربح ÷ سعر البيع النهائي', targetPrice:'سعر البيع المستهدف', targetFixed:'هدف ربح ثابت', targetPercent:'هدف بالنسبة المئوية',
    noProducts:'قرارك التجاري التالي يبدأ هنا.', emptyCopy:'أضف منتجاً لمعرفة تكلفته الحقيقية وسعر التعادل والربح قبل البيع.', startAdding:'أضف منتجك الأول', productList:'منتجاتك', productListCopy:'صورة واضحة لما تبيعه وما تربحه.', searchPlaceholder:'ابحث عن المنتجات...',
    chartTitle:'الربح حسب العملة', chartSubtitle:'نتائجك المسجلة، مع فصل كل عملة.', recentActivity:'أحدث الحسابات', noActivity:'ستظهر حساباتك هنا.', quickCalculator:'حاسبة سريعة', quickCopy:'ابدأ بسعر وسنساعدك على رؤية الصورة كاملة.', openLab:'افتح مختبر التسعير',
    stepInfo:'معلومات المنتج', stepExpenses:'المصاريف', stepPricing:'التسعير', stepReview:'المراجعة', name:'اسم المنتج', category:'الفئة (اختياري)', currency:'العملة', unitCost:'تكلفة شراء القطعة', quantity:'الكمية المشتراة', weight:'وزن المنتج (اختياري)',
    expenseName:'اسم المصروف', amount:'المبلغ', addExpense:'أضف مصروفاً', noExpenses:'لم تتم إضافة مصاريف خاصة بالمنتج.', expenseHelp:'أدخل المصاريف التي يدفعها البائع فقط. لا تخصم توصيل العميل.', directExpense:'مصروف خاص بالمنتج', expenseLabel:'مثال: التغليف', purchaseDetails:'تفاصيل الشراء', pricingDetails:'تفاصيل التسعير', reviewNote:'راجع التفاصيل. سيُسجل الحساب بعد الحفظ.',
    totalPurchase:'إجمالي تكلفة الشراء', allocatedExpenses:'مصاريف إضافية', finalPrice:'السعر النهائي بعد الخصم', targetBasis:'تعني النسبة المستهدفة', marginBasis:'الربح ÷ سعر البيع (هامش)', markupBasis:'الربح ÷ إجمالي التكلفة (زيادة)',
    allCurrencies:'كل العملات', noResults:'لا توجد منتجات تطابق البحث.', edit:'تعديل', delete:'حذف', confirmDelete:'حذف المنتج وسيناريوهاته؟ ستتم إعادة توزيع المصاريف المشتركة على المنتجات المتبقية.', saved:'تم حفظ المنتج وتسجيل الحساب.', updated:'تم تحديث المنتج.', deleted:'تم حذف المنتج.',
    infoTitle:'معلومات المنتج', expenseBreakdown:'تفاصيل التكلفة', scenarioCompare:'قارن سيناريوهات التسعير', addScenario:'أضف سيناريو', noScenarios:'لا توجد سيناريوهات بعد. أضف أسعاراً للمقارنة.',
    scenario:'السيناريو', price:'السعر الأصلي', discountShort:'الخصم', finalUnit:'سعر القطعة النهائي', wholeProfit:'إجمالي الربح / الخسارة', needed:'السعر المطلوب', deleteConfirm:'هل تريد حذف هذا السيناريو؟', scenarioSaved:'تم حفظ السيناريو.', settingsTitle:'تفضيلاتك', language:'اللغة', appearance:'المظهر', lightMode:'الوضع الفاتح', darkMode:'الوضع الداكن', accountTitle:'حسابك', guestInfo:'تستخدم مساحة ضيف. تُحفظ البيانات في قاعدة التطبيق المحلية على هذا الجهاز.', createAccountAction:'أنشئ حساباً', logout:'تسجيل الخروج',
    activityTitle:'سجل الحسابات', activityCopy:'سجل للحسابات التي أكّدتها.', date:'التاريخ', inputSummary:'المدخلات', result:'النتيجة', suggestions:'اقترح تحسينات الربح', suggestionsTitle:'أفكار للمراجعة', suggestionsLimit:'هذه مقارنات حسابية فقط، ولا تتنبأ بطلب العملاء أو حجم المبيعات.', noSuggestions:'لا يتوفر سعر مقارنة أعلى مع السعر والخصم الحاليين.', suggestionAlreadyHigh:'السعر الحالي يساوي سعر المقارنة أو يتجاوزه.', suggestionNoBreakEven:'الخصم الكامل لا يتيح تحديد سعر تعادل للمقارنة.', aiReview:'مراجعة مالية بالذكاء الاصطناعي', aiConsent:'سيتم إرسال مدخلات هذا المنتج ونتائجه المالية إلى OpenAI للمراجعة. هل تريد المتابعة؟', aiDisclaimer:'قد تكون تعليقات الذكاء الاصطناعي غير دقيقة. الأرقام أعلاه محسوبة محلياً وهي المرجع.', aiUnavailable:'مراجعة الذكاء الاصطناعي غير مهيأة على هذا الخادم.',
    required:'يرجى تعبئة الحقول المطلوبة.', invalidVoice:'تعذر فهم بعض القيم. راجعها وأدخل التفاصيل الناقصة بنفسك.', unsupportedVoice:'الإدخال الصوتي غير متاح في هذا المتصفح. جرّب Chrome أو Edge.', permissionVoice:'تم منع الوصول إلى الميكروفون. اسمح به من إعدادات المتصفح وحاول مجدداً.', recording:'جارٍ الاستماع… تحدث بطبيعية ثم أوقف التسجيل للمراجعة.', stoppingVoice:'جارٍ إنهاء التعرف على الكلام…', stoppedVoice:'توقف التسجيل. راجع الحقول التي تم التقاطها.', noSpeechVoice:'لم يتم اكتشاف كلام. حاول مجدداً أو أدخل التفاصيل يدوياً.', networkVoice:'خدمة التعرف على الكلام غير متاحة. تحقق من الاتصال وحاول مجدداً.', microphoneVoice:'لم يتم العثور على ميكروفون. تحقق من الجهاز وحاول مجدداً.', stoppingVoice:'جارٍ إنهاء التعرف على الكلام…', stoppedVoice:'توقف التسجيل. راجع الحقول التي تم التقاطها.', noSpeechVoice:'لم يتم اكتشاف كلام. حاول مجدداً أو أدخل التفاصيل يدوياً.', networkVoice:'خدمة التعرف على الكلام غير متاحة. تحقق من الاتصال وحاول مجدداً.', microphoneVoice:'لم يتم العثور على ميكروفون. تحقق من الجهاز وحاول مجدداً.', transcribed:'تم تحويل الكلام. راجع الحقول المظللة قبل المتابعة.', voiceError:'توقف الإدخال الصوتي. يمكنك إدخال البيانات يدوياً.', loading:'جارٍ التحميل…', error:'حدث خطأ. حاول مرة أخرى.',
    ltr:'English', rtl:'العربية', settingsSaved:'تم حفظ التفضيل.', targetMeaning:'مقام النسبة المستهدفة واضح ويمكن تغييره.', noHistory:'لم يتم تسجيل أي حساب بعد.', currencyTotals:'الإجمالي حسب العملة', other:'أخرى', cost:'التكلفة', unit:'قطعة', fixed:'ثابت', percentage:'نسبة', choose:'اختر…', item:'عنصر', expensesHeading:'مصاريف إضافية', step:'الخطوة', close:'إغلاق', googleContinue:'المتابعة باستخدام Google', googleUnavailable:'تسجيل الدخول عبر Google غير مهيأ على هذا الخادم بعد.', googleFailed:'تعذر إكمال تسجيل الدخول عبر Google. حاول مجدداً.', googleCancelled:'تم إلغاء تسجيل الدخول عبر Google.', or:'أو', sharedExpenseTitle:'مصروف مشترك', sharedExpenseSubtitle:'اختر المنتجات بنفس العملة وطريقة التوزيع.', sharedExpenseBasis:'أساس التوزيع', sharedExpenseNote:'لا توجد قاعدة خاصة لشحن المورد إلى البائع. أضفه فقط كمصروف مشترك عام بأساس صريح. لا يُخصم توصيل العميل من أرباحك.', allocateExpense:'توزيع المصروف', sharedPlaceholder:'أجور المورد، تغليف مشترك…', sharedAction:'مصاريف مشتركة',
  }
};

const state = { lang: localStorage.getItem('ml-lang') || 'en', theme: localStorage.getItem('ml-theme') || 'light', route: 'dashboard', session: null, products: [], history: [], step: 0, draft: {}, quickDraft:null, editing: null, activeProduct: null, detailTab: 'info', recognition: null, recording: false, voiceStarting:false, voiceStopping:false, voiceAbort:false, voiceTranscript:'', voiceErrorMessage:'', authMode: 'signup', search: '', currencyFilter: '', suggestions: false, aiAvailable:false, aiReview:null, savingProduct:false, pendingSavedProduct:null };
const $ = (selector, root=document) => root.querySelector(selector);
const $$ = (selector, root=document) => [...root.querySelectorAll(selector)];
const t = key => words[state.lang][key] || words.en[key] || key;
const moneyFmt = (amount, currency='USD') => new Intl.NumberFormat(state.lang === 'ar' ? 'ar' : 'en', { style:'currency', currency, minimumFractionDigits:2, maximumFractionDigits:2 }).format(Number(amount || 0));
const numberFmt = amount => new Intl.NumberFormat(state.lang === 'ar' ? 'ar' : 'en', { maximumFractionDigits:2 }).format(Number(amount || 0));

async function api(path, options={}) {
  const headers = { ...(options.headers || {}) };
  if (options.body !== undefined) headers['Content-Type'] = 'application/json';
  if (options.method && options.method !== 'GET' && state.csrf) headers['X-CSRF-Token'] = state.csrf;
  const response = await fetch(path, { credentials:'same-origin', ...options, headers, body: options.body === undefined ? undefined : JSON.stringify(options.body) });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.error || t('error'));
  if (data.csrf) state.csrf = data.csrf;
  return data;
}

function setLocale() {
  const quickForm=$('#quickCalcForm');
  if(quickForm) state.quickDraft=Object.fromEntries(new FormData(quickForm).entries());
  document.documentElement.lang = state.lang;
  document.documentElement.dir = state.lang === 'ar' ? 'rtl' : 'ltr';
  document.body.dataset.theme = state.theme;
  localStorage.setItem('ml-lang', state.lang); localStorage.setItem('ml-theme', state.theme);
  $$('[data-i18n]').forEach(el => el.textContent = t(el.dataset.i18n));
  $$('[data-i18n-placeholder]').forEach(el => el.placeholder = t(el.dataset.i18nPlaceholder));
  $('#languageToggle').textContent = state.lang === 'en' ? 'ع' : 'EN';
  $('#searchInput').placeholder = t('searchPlaceholder');
  renderPage();
}

async function loadWorkspace() {
  const [products, history] = await Promise.all([api('/api/products'), api('/api/history')]);
  state.products = products; state.history = history;
  $('#productCount').textContent = products.length;
  renderPage(); updateProfile();
}

function updateProfile() {
  const email = state.session?.profile?.email;
  const displayName = state.session?.profile?.display_name || email || null;
  $('#profileName').textContent = displayName || (state.lang === 'ar' ? 'مساحة الضيف' : 'Guest workspace');
  $('#profileMode').textContent = email || (state.lang === 'ar' ? 'مساحة عمل محلية' : 'Local workspace');
  $('#avatarInitial').textContent = (email || 'G').charAt(0).toUpperCase(); $('#topProfile').textContent = (email || 'G').charAt(0).toUpperCase();
}

function showToast(message, type='success') {
  const toast = document.createElement('div'); toast.className = `toast toast-${type}`; toast.innerHTML = `<span>${type === 'success' ? '✓' : '!'}</span><p></p>`; $('p', toast).textContent = message; $('#toastRegion').append(toast);
  setTimeout(() => toast.classList.add('toast-out'), 2800); setTimeout(() => toast.remove(), 3200);
}

function profitClass(result) { return result?.status === 'profit' ? 'positive' : result?.status === 'loss' ? 'negative' : 'neutral'; }
function statusPill(result) { const status=result?.status || 'break_even'; return `<span class="status-pill ${profitClass(result)}"><i></i>${t(status)}</span>`; }
function productCard(product, compact=false) {
  const result=product.result || {};
  return `<article class="product-card ${compact?'product-card-compact':''}" data-product-card="${product.id}" tabindex="0" role="button" aria-label="${escapeHtml(product.name)}">
    <div class="card-topline"><span class="product-glyph">${safeInitial(product.name)}</span><button class="mini-more" data-card-menu="${product.id}" aria-label="More options">···</button></div>
    <div class="product-card-name">${escapeHtml(product.name)}</div><div class="product-card-category">${escapeHtml(product.category || t('products'))}</div>
    <div class="product-card-price"><span>${t('sellingPrice')}</span><strong>${moneyFmt(result.final_unit_price || 0, product.currency)}</strong></div>
    <div class="product-card-bottom"><span class="product-profit ${profitClass(result)}">${moneyFmt(result.profit || 0, product.currency)} <small>${t(result.status || 'breakEven')}</small></span>${statusPill(result)}</div>
  </article>`;
}
function safeInitial(name='') { return escapeHtml(String(name || '').trim().charAt(0).toUpperCase() || '✦'); }
function escapeHtml(value='') { return String(value ?? '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch])); }

function renderPage() {
  const pages = { dashboard:renderDashboard, products:renderProducts, calculator:renderCalculator, history:renderHistory, settings:renderSettings };
  const headings = { dashboard:t('dashboard'), products:t('products'), calculator:t('calculator'), history:t('history'), settings:t('settings') };
  $('#pageHeading').textContent = headings[state.route] || t('dashboard');
  $$('.nav-item[data-route]').forEach(button => button.classList.toggle('active', button.dataset.route === state.route));
  $('#pageContent').innerHTML = (pages[state.route] || renderDashboard)();
  bindPageActions();
}

function renderDashboard() {
  if (!state.products.length) return `<section class="welcome-row"><div><div class="eyebrow">${t('dashboard').toUpperCase()}</div><h1>${t('goodMorning')}${state.lang==='ar'?'، ':', '}<span>${state.session?.profile?.display_name ? escapeHtml(state.session.profile.display_name) : state.session?.profile?.display_name ? escapeHtml(state.session.profile.display_name) : state.session?.profile?.email ? escapeHtml(state.session.profile.email.split('@')[0]) : (state.lang==='ar'?'صديقتنا':'there')}</span> <b>✦</b></h1><p>${t('overview')}</p></div><button class="button button-primary" data-action="add">${t('addProduct')} <span>＋</span></button></section><section class="empty-hero"><div class="empty-art"><div class="orbit orbit-one"></div><div class="orbit orbit-two"></div><div class="empty-calculator"><span>∑</span><i></i><i></i><i></i><strong>↗</strong></div><div class="float-dot float-a">✦</div><div class="float-dot float-b">●</div></div><div class="empty-text"><span class="eyebrow">${t('quickCalculator')}</span><h2>${t('noProducts')}</h2><p>${t('emptyCopy')}</p><button class="button button-primary" data-action="add">${t('startAdding')} <span>→</span></button><button class="text-button empty-calc" data-route-link="calculator">${t('openLab')} ↗</button></div></section><section class="bottom-grid"><div class="panel soft-panel"><div class="panel-head"><div><h3>${t('chartTitle')}</h3><p>${t('chartSubtitle')}</p></div><span class="chart-period">${state.lang==='ar'?'الآن':'LIVE'}</span></div><div class="chart-empty"><span>⌁</span><p>${t('noActivity')}</p></div></div><div class="panel quick-panel"><span class="quick-icon">⌗</span><h3>${t('quickCalculator')}</h3><p>${t('quickCopy')}</p><button class="button button-light" data-route-link="calculator">${t('openLab')} ↗</button></div></section>`;
  const byCurrency = currencySummary();
  const productCount=state.products.length, totalProfit=Object.keys(byCurrency).length===1 ? Object.values(byCurrency)[0].profit : null;
  const marginsByCurrency=Object.fromEntries(Object.keys(byCurrency).map(currency=>{const margins=state.products.filter(p=>p.currency===currency).map(p=>p.result?.margin_percent).filter(v=>v!==null&&v!==undefined&&Number.isFinite(Number(v))).map(Number);return [currency,margins.length?margins.reduce((a,b)=>a+b,0)/margins.length:null];}));
  const averageMargin=Object.keys(marginsByCurrency).length===1?Object.values(marginsByCurrency)[0]:null;
  const marginSummary=Object.entries(marginsByCurrency).map(([currency,value])=>`${currency} ${value===null?'—':`${numberFmt(value)}%`}`).join(' · ');
  return `<section class="welcome-row"><div><div class="eyebrow">${t('dashboard').toUpperCase()}</div><h1>${t('goodMorning')}${state.lang==='ar'?'، ':', '}<span>${state.session?.profile?.email ? escapeHtml(state.session.profile.email.split('@')[0]) : (state.lang==='ar'?'صديقتنا':'there')}</span> <b>✦</b></h1><p>${t('overview')}</p></div><button class="button button-primary" data-action="add">${t('addProduct')} <span>＋</span></button></section>
  <section class="summary-grid"><article class="summary-card summary-purple"><div class="summary-label">${t('totalProducts')}<span class="summary-icon">▧</span></div><strong>${numberFmt(productCount)}</strong><small>${t('allProducts')}</small><div class="summary-decoration">▧</div></article><article class="summary-card"><div class="summary-label">${t('profitThisMonth')}<span class="summary-icon green-icon">↗</span></div><strong>${totalProfit===null?'—':moneyFmt(totalProfit,Object.keys(byCurrency)[0])}</strong><small>${Object.keys(byCurrency).length>1?t('currencyTotals'):t('profit')}</small></article><article class="summary-card"><div class="summary-label">${t('averageMargin')}<span class="summary-icon lavender-icon">％</span></div><strong>${averageMargin===null?'—':`${numberFmt(averageMargin)}%`}</strong><small>${marginSummary||t('margin')}</small></article><article class="summary-card"><div class="summary-label">${t('calculations')}<span class="summary-icon peach-icon">◷</span></div><strong>${numberFmt(state.history.length)}</strong><small>${t('recentActivity')}</small></article></section>
  <section class="panel chart-panel"><div class="panel-head"><div><h3>${t('chartTitle')}</h3><p>${t('chartSubtitle')}</p></div><span class="legend-chip"><i></i>${t('profit')} / ${t('loss')}</span></div>${renderCurrencyChart(state.history)}</section>
  <section class="panel products-panel"><div class="panel-head"><div><h3>${t('recentProducts')}</h3><p>${t('allProducts')}</p></div><button class="text-button" data-route-link="products">${t('viewAll')} ↗</button></div><div class="product-grid">${state.products.slice(0,4).map(p=>productCard(p,true)).join('')}</div></section>
  <section class="bottom-grid"><div class="panel activity-panel"><div class="panel-head"><div><h3>${t('recentActivity')}</h3><p>${t('activityCopy')}</p></div><button class="text-button" data-route-link="history">${t('viewAll')} ↗</button></div>${state.history.length?state.history.slice(0,4).map(historyRow).join(''):`<div class="mini-empty">${t('noActivity')}</div>`}</div><div class="panel quick-panel"><span class="quick-icon">✦</span><h3>${t('quickCalculator')}</h3><p>${t('quickCopy')}</p><button class="button button-light" data-route-link="calculator">${t('openLab')} ↗</button></div></section>`;
}

function currencySummary() {
  const summary={};
  for(const product of state.products){ const c=product.currency || 'USD', r=product.result || {}; summary[c] ||= {profit:0,revenue:0,cost:0,count:0}; summary[c].profit += Number(r.profit || 0); summary[c].revenue += Number(r.revenue || 0); summary[c].cost += Number(r.total_cost || 0); summary[c].count++; }
  return summary;
}
function renderCurrencyChart(summary) {
  const currencies=[...new Set(summary.map(item=>item.inputs?.currency).filter(Boolean))]; if(!currencies.length) return `<div class="chart-empty"><span>⌁</span><p>${t('noActivity')}</p></div>`;
  const now=new Date(); const months=Array.from({length:6},(_,index)=>new Date(now.getFullYear(),now.getMonth()-5+index,1));
  return `<div class="trend-charts">${currencies.map(currency=>{const totals=months.map(month=>summary.filter(item=>{const d=new Date((item.created_at||0)*1000);return item.inputs?.currency===currency&&d.getFullYear()===month.getFullYear()&&d.getMonth()===month.getMonth();}).reduce((sum,item)=>sum+Number(item.result?.profit||0),0));const max=Math.max(...totals.map(Math.abs),1);return `<div class="trend-currency"><div class="trend-title"><strong>${currency}</strong><span>${moneyFmt(totals.reduce((a,b)=>a+b,0),currency)} ${t('profit').toLowerCase()}</span></div><div class="trend-bars">${months.map((month,index)=>{const value=totals[index],height=value?Math.min(60,Math.max(10,Math.round(Math.abs(value)/max*60/10)*10)):0;return `<div class="trend-point"><span class="trend-value ${value<0?'negative':''}">${value?moneyFmt(value,currency):''}</span><div class="trend-well"><i class="trend-size-${height} ${value<0?'bar-loss':''}"></i></div><small>${escapeHtml(new Intl.DateTimeFormat(state.lang==='ar'?'ar':'en',{month:'short'}).format(month))}</small></div>`;}).join('')}</div></div>`;}).join('')}</div>`;
}
function renderProducts() {
  const filtered=state.products.filter(p=>{
    const matchSearch=`${p.name} ${p.category} ${p.currency}`.toLowerCase().includes(state.search.toLowerCase());
    const matchCurrency=!state.currencyFilter||p.currency===state.currencyFilter;
    return matchSearch && matchCurrency;
  });
  const currencies=[...new Set(state.products.map(p=>p.currency))];
  return `<section class="page-title-row"><div><div class="eyebrow">${t('workspace')}</div><h1>${t('productList')}</h1><p>${t('productListCopy')}</p></div><div class="title-actions"><button class="button button-secondary" data-action="shared">⇄ ${t('sharedAction')}</button><button class="button button-primary" data-action="add">${t('addProduct')} <span>＋</span></button></div></section>${state.products.length?`<div class="filter-row"><span class="filter-caption">${numberFmt(filtered.length)} ${t('products').toLowerCase()}</span><select id="currencyFilter" class="select-filter"><option value="">${t('allCurrencies')}</option>${currencies.map(c=>`<option value="${c}" ${state.currencyFilter===c?'selected':''}>${c}</option>`).join('')}</select></div><div class="product-grid product-grid-large" id="productGrid">${filtered.map(p=>productCard(p)).join('') || `<div class="mini-empty">${t('noResults')}</div>`}</div>`:`<div class="empty-products"><div class="empty-icon">▧</div><h2>${t('noProducts')}</h2><p>${t('emptyCopy')}</p><button class="button button-primary" data-action="add">${t('startAdding')} ＋</button></div>`}`;
}
function renderCalculator() {
  const sample=state.quickDraft||state.products[0];
  return `<section class="page-title-row"><div><div class="eyebrow">${t('pricingLab')}</div><h1>${t('quickCalculator')}</h1><p>${t('quickCopy')}</p></div><button class="button button-primary" data-action="add">${t('addProduct')} ＋</button></section><div class="calculator-layout"><div class="panel calculator-panel"><div class="panel-head"><div><h3>${t('pricingDetails')}</h3><p>${t('targetMeaning')}</p></div><span class="quick-icon">⌗</span></div><form id="quickCalcForm"><div class="form-grid"><label class="field span-2"><span>${t('name')}</span><input name="name" value="${escapeHtml(sample?.name||'')}" placeholder="${t('name')}" required></label><label class="field"><span>${t('currency')}</span>${currencySelect(sample?.currency || 'USD')}</label><label class="field"><span>${t('quantity')}</span><input name="quantity" type="number" min="1" step="1" value="${sample?.quantity||1}" required></label><label class="field"><span>${t('unitCost')}</span><input name="unit_cost" type="number" min="0" step="0.01" value="${sample?.unit_cost||''}" required></label><label class="field"><span>${t('sellingPrice')}</span><input name="selling_price" type="number" min="0" step="0.01" value="${sample?.selling_price||''}" required></label><label class="field"><span>${t('discount')}</span><div class="input-suffix"><input name="discount_percent" type="number" min="0" max="100" step="0.01" value="${sample?.discount_percent??0}"><span>%</span></div></label><label class="field"><span>${t('targetBasis')}</span><select name="target_basis"><option value="margin" ${(sample?.target_basis||'margin')==='margin'?'selected':''}>${t('marginBasis')}</option><option value="markup" ${sample?.target_basis==='markup'?'selected':''}>${t('markupBasis')}</option></select></label><label class="field"><span>${t('targetFixed')}</span><input name="target_profit_amount" type="number" min="0" step="0.01" value="${sample?.target_profit_amount??0}"></label><label class="field"><span>${t('targetPercent')}</span><div class="input-suffix"><input name="target_profit_percent" type="number" min="0" max="10000" step="0.01" value="${sample?.target_profit_percent??20}"><span>%</span></div></label></div><div class="calc-form-foot"><span>✓ ${state.lang==='ar'?'الحسابات محددة ولا تستخدم تحويل العملات':'Calculations are deterministic. No currency conversion.'}</span><button class="button button-primary" type="submit">${state.lang==='ar'?'احسب النتيجة':'Calculate result'} <span>→</span></button></div></form></div><div class="panel calc-result-panel" id="quickCalcResult"><div class="result-placeholder"><span>∑</span><h3>${state.lang==='ar'?'نتيجتك ستظهر هنا':'Your result will appear here'}</h3><p>${t('quickCopy')}</p></div></div></div>`;
}
function renderHistory() {
  return `<section class="page-title-row"><div><div class="eyebrow">${t('workspace')}</div><h1>${t('activityTitle')}</h1><p>${t('activityCopy')}</p></div></section><div class="panel history-panel"><div class="history-header"><span>${t('date')}</span><span>${t('inputSummary')}</span><span>${t('result')}</span><span></span></div>${state.history.length?state.history.map(historyRow).join(''):`<div class="empty-products"><div class="empty-icon">◷</div><h2>${t('noHistory')}</h2><p>${t('activityCopy')}</p></div>`}</div>`;
}
function historyRow(item) {
  const p=state.products.find(x=>x.id===item.product_id), data=item.inputs || {}, result=item.result || {}; const when=new Date((item.created_at||Date.now()/1000)*1000);
  return `<div class="history-row"><span class="history-date">${escapeHtml(new Intl.DateTimeFormat(state.lang==='ar'?'ar':'en',{month:'short',day:'numeric',hour:'2-digit',minute:'2-digit'}).format(when))}</span><span class="history-product"><i class="history-glyph">∑</i><span><strong>${escapeHtml(data.name||p?.name||t('item'))}</strong><small>${t('quantity')}: ${numberFmt(data.quantity||0)} · ${moneyFmt(data.selling_price||0,data.currency||p?.currency||'USD')}</small></span></span><span class="history-result ${profitClass(result)}"><strong>${moneyFmt(result.profit||0,data.currency||p?.currency||'USD')}</strong><small>${t(result.status||'breakEven')}</small></span>${item.product_id?`<button class="row-open" data-open-product="${item.product_id}" aria-label="Open product">↗</button>`:`<span class="row-open-placeholder"></span>`}</div>`;
}
function renderSettings() {
  return `<section class="page-title-row"><div><div class="eyebrow">${t('workspace')}</div><h1>${t('settingsTitle')}</h1><p>${t('targetMeaning')}</p></div></section><div class="settings-layout"><section class="panel settings-panel"><div class="settings-section"><div class="settings-icon">文</div><div class="settings-copy"><h3>${t('language')}</h3><p>${state.lang==='ar'?'بدّل بين العربية والإنجليزية':'Choose your display language and reading direction.'}</p></div><div class="segmented"><button data-lang="en" class="${state.lang==='en'?'selected':''}">English</button><button data-lang="ar" class="${state.lang==='ar'?'selected':''}">العربية</button></div></div><div class="settings-section"><div class="settings-icon">◐</div><div class="settings-copy"><h3>${t('appearance')}</h3><p>${state.lang==='ar'?'اختر المظهر المريح لك':'Choose a comfortable display theme.'}</p></div><div class="segmented"><button data-theme="light" class="${state.theme==='light'?'selected':''}">☼ ${t('lightMode')}</button><button data-theme="dark" class="${state.theme==='dark'?'selected':''}">◐ ${t('darkMode')}</button></div></div><div class="settings-section"><div class="settings-icon">◉</div><div class="settings-copy"><h3>${t('accountTitle')}</h3><p>${state.session?.profile?escapeHtml(state.session.profile.email):t('guestInfo')}</p></div><button class="button button-secondary" data-action="auth">${state.session?.profile?t('logout'):t('createAccountAction')}</button></div><div class="settings-section"><div class="settings-icon">⌁</div><div class="settings-copy"><h3>${state.lang==='ar'?'الإدخال الصوتي':'Voice input'}</h3><p>${state.lang==='ar'?'يستخدم التعرف على الكلام في المتصفح. قد يُرسل الصوت إلى مزود خدمة المتصفح. لا يحتفظ التطبيق بالتسجيل.':'Uses your browser speech recognizer. Audio may be processed by your browser provider. This app does not retain recordings.'}</p></div></div><div class="settings-section"><div class="settings-icon">✦</div><div class="settings-copy"><h3>${state.lang==='ar'?'الاقتراحات':'Suggestions'}</h3><p>${state.lang==='ar'?'اقتراحات تحسين الربح تستخدم الحسابات فقط ولا تتنبأ بالطلب.':'Improvement suggestions compare arithmetic only; they do not predict demand.'}</p></div></div></section><aside class="panel about-panel"><span class="brand-mark">m</span><h3>CostPilot<span class="brand-dot">.</span></h3><p>${state.lang==='ar'?'مختبر قرار التكلفة والربح والتسعير':'Product cost, profit & pricing decision lab'}</p><div class="about-separator"></div><small>v1.0 · Local workspace</small></aside></div>`;
}

function currencySelect(selected='USD') { return `<select name="currency" required>${CURRENCIES.map(c=>`<option value="${c}" ${c===selected?'selected':''}>${c} · ${currencySymbols[c]}</option>`).join('')}</select>`; }
function bindPageActions() {
  $$('[data-action="add"]').forEach(b=>b.onclick=()=>openWizard());
  $$('[data-action="auth"]').forEach(b=>b.onclick=()=>{if(state.session?.profile) logout();else openAuth('signup');});
  $$('[data-route-link]').forEach(b=>b.onclick=()=>navigate(b.dataset.routeLink));
  $$('[data-product-card]').forEach(card=>{card.onclick=e=>{if(e.target.closest('[data-card-menu]'))return;openProduct(card.dataset.productCard);};card.onkeydown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();openProduct(card.dataset.productCard);}};});
  $$('[data-card-menu]').forEach(b=>b.onclick=e=>{e.stopPropagation();const p=state.products.find(x=>x.id===b.dataset.cardMenu);if(p)openProduct(p.id);});
  $$('[data-open-product]').forEach(b=>b.onclick=()=>b.dataset.openProduct&&openProduct(b.dataset.openProduct));
  $('#currencyFilter')?.addEventListener('change',e=>{state.currencyFilter=e.target.value;renderPage();});
  const quickForm=$('#quickCalcForm');
  if(quickForm){
    quickForm.onsubmit=quickCalculate;
    const calculateButton=quickForm.querySelector('button[type="submit"]');
    calculateButton.onclick=event=>{
      event.preventDefault();
      if(quickForm.reportValidity()) quickCalculate({target:quickForm,currentTarget:quickForm,preventDefault(){}});
    };
  }
  $$('[data-lang]').forEach(b=>b.onclick=()=>{state.lang=b.dataset.lang;setLocale();}); $$('[data-theme]').forEach(b=>b.onclick=()=>{state.theme=b.dataset.theme;setLocale();});
}
function navigate(route) { state.route=route; $('#sidebar').classList.remove('sidebar-open'); $('#scrim').classList.remove('visible'); if(matchMedia('(max-width: 850px)').matches) $('#mobileMenu').setAttribute('aria-expanded','false'); renderPage(); window.scrollTo({top:0,behavior:'smooth'}); }

function stepFields(step) {
  const d=state.draft, en=state.lang==='en';
  if(step===0) return `<div class="form-grid"><label class="field span-2"><span>${t('name')} *</span><input name="name" maxlength="120" value="${escapeHtml(d.name||'')}" required placeholder="${en?'e.g. Ceramic cup':'مثال: كوب خزفي'}"></label><label class="field"><span>${t('category')}</span><input name="category" maxlength="80" value="${escapeHtml(d.category||'')}" placeholder="${en?'Home & living':'منزل ومعيشة'}"></label><label class="field"><span>${t('currency')} *</span>${currencySelect(d.currency||'USD')}</label><label class="field"><span>${t('unitCost')} *</span><input name="unit_cost" type="number" min="0" step="0.01" value="${d.unit_cost??''}" required placeholder="0.00"></label><label class="field"><span>${t('quantity')} *</span><input name="quantity" type="number" min="1" step="1" value="${d.quantity??1}" required></label><label class="field"><span>${t('weight')}</span><input name="weight" type="number" min="0" step="0.001" value="${d.weight??''}" placeholder="${en?'For weight-based sharing':'للتوزيع حسب الوزن'}"></label></div>`;
  if(step===1) return `<div class="expense-intro"><div class="expense-illustration">↗</div><div><h3>${t('expensesHeading')}</h3><p>${t('expenseHelp')}</p></div></div><div id="expenseRows">${(d.expenses||[]).map((e,i)=>expenseRow(e,i)).join('')}</div><button type="button" class="button button-secondary add-expense-button" id="addExpenseButton">＋ ${t('addExpense')}</button><div class="expense-note"><span>ⓘ</span>${t('directExpense')}</div>`;
  if(step===2) return `<div class="form-grid"><label class="field"><span>${t('sellingPrice')} *</span><div class="currency-input"><span>${currencySymbols[d.currency||'USD']}</span><input name="selling_price" type="number" min="0" step="0.01" value="${d.selling_price??''}" required placeholder="0.00"></div></label><label class="field"><span>${t('discount')}</span><div class="input-suffix"><input name="discount_percent" type="number" min="0" max="100" step="0.01" value="${d.discount_percent??0}"><span>%</span></div></label><div class="form-section-label span-2">${t('targetPrice')}</div><label class="field"><span>${t('targetFixed')}</span><input name="target_profit_amount" type="number" min="0" step="0.01" value="${d.target_profit_amount??0}"></label><label class="field"><span>${t('targetPercent')}</span><div class="input-suffix"><input name="target_profit_percent" type="number" min="0" max="10000" step="0.01" value="${d.target_profit_percent??20}"><span>%</span></div></label><label class="field span-2"><span>${t('targetBasis')}</span><select name="target_basis"><option value="margin" ${(d.target_basis||'margin')==='margin'?'selected':''}>${t('marginBasis')}</option><option value="markup" ${d.target_basis==='markup'?'selected':''}>${t('markupBasis')}</option></select><small>${t('targetMeaning')}</small></label><div class="pricing-note span-2"><span>✦</span><span>${state.lang==='ar'?'الخصم الذي تدخله فقط هو الذي يُطبق. لا يخصم توصيل العميل من ربح البائع.':'Only the discount you enter is applied. Customer-paid delivery is not deducted from seller profit.'}</span></div></div>`;
  return reviewMarkup(d);
}
function expenseRow(expense={},index=0) { return `<div class="expense-row" data-index="${index}"><label class="field"><span>${t('expenseName')}</span><input data-expense-name value="${escapeHtml(expense.name||'')}" placeholder="${t('expenseLabel')}"></label><label class="field"><span>${t('amount')}</span><input data-expense-amount type="number" min="0" step="0.01" value="${expense.amount??''}" placeholder="0.00"></label><button type="button" class="remove-expense" aria-label="${t('delete')}" data-remove-expense>×</button></div>`; }
function reviewMarkup(d) {
  const currency=d.currency||'USD';
  return `<div class="review-banner"><span>✓</span><div><strong>${t('stepReview')}</strong><p>${t('reviewNote')}</p></div></div><div class="review-product-head"><span class="product-glyph">${safeInitial(d.name)}</span><div><strong>${escapeHtml(d.name||'—')}</strong><small>${escapeHtml(d.category||t('products'))} · ${currency}</small></div></div><div class="review-metrics"><div><span>${t('unitCost')}</span><strong>${moneyFmt(d.unit_cost||0,currency)}</strong></div><div><span>${t('quantity')}</span><strong>${numberFmt(d.quantity||0)} ${t('unit')}</strong></div><div><span>${t('price')}</span><strong>${moneyFmt(d.selling_price||0,currency)}</strong></div><div><span>${t('discount')}</span><strong>${numberFmt(d.discount_percent||0)}%</strong></div></div><div class="review-expenses">${(d.expenses||[]).filter(e=>e.name||e.amount).map(e=>`<div><span>${escapeHtml(e.name||t('expenseName'))}</span><strong>${moneyFmt(e.amount||0,currency)}</strong></div>`).join('') || `<span>${t('noExpenses')}</span>`}</div>`;
}
function openWizard(product=null) {
  state.editing=product?.id||null; state.pendingSavedProduct=null; state.savingProduct=false; state.step=0; state.draft=product?JSON.parse(JSON.stringify(product)):{currency:'USD',quantity:1,discount_percent:0,target_profit_amount:0,target_profit_percent:20,target_basis:'margin',expenses:[]};
  $('#wizardTitle').textContent=product?t('editProduct'):t('addProductTitle'); $('#voiceStatus').textContent=''; $('#wizardDialog').showModal(); renderWizardStep();
}
function captureStep() {
  const body=$('#wizardBody'), form=$('#productForm');
  $$('[name]',body).forEach(el=>{if(el.name==='currency'||el.name==='target_basis')state.draft[el.name]=el.value;else state.draft[el.name]=el.value;});
  if(state.step===1) state.draft.expenses=$$('.expense-row',body).map(row=>({name:$('[data-expense-name]',row).value,amount:$('[data-expense-amount]',row).value,allocation:'direct'})).filter(e=>e.name.trim()||e.amount!=='');
  const required=$$('[required]',body).find(el=>!el.checkValidity());
  if(required){required.reportValidity();return false;}
  return true;
}
function renderWizardStep() {
  const labels=['stepInfo','stepExpenses','stepPricing','stepReview'];
  $('#stepper').innerHTML=labels.map((key,i)=>`<div class="step-item ${i===state.step?'current':i<state.step?'completed':''}"><span class="step-circle">${i<state.step?'✓':i+1}</span><span>${t(key)}</span></div>${i<labels.length-1?'<i class="step-line"></i>':''}`).join('');
  $('#wizardBody').innerHTML=stepFields(state.step); $('#stepBack').style.visibility=state.step===0?'hidden':'visible';
  const nextKey=state.step>=3?(state.editing?'saveChanges':'saveCalculate'):'continue';
  $('#stepNext').dataset.i18n=nextKey;
  $('#stepNext').innerHTML=state.step>=3?`${t(nextKey)} <span>✓</span>`:`${t(nextKey)} <span>${state.lang==='ar'?'←':'→'}</span>`;
  $('#stepCaption').textContent=`${t('step')} ${numberFmt(state.step+1)} / 4`;
  $('#addExpenseButton')?.addEventListener('click',()=>{state.draft.expenses=$$('.expense-row').map(row=>({name:$('[data-expense-name]',row).value,amount:$('[data-expense-amount]',row).value}));state.draft.expenses.push({});renderWizardStep();});
  $$('[data-remove-expense]').forEach(btn=>btn.onclick=()=>{state.draft.expenses=$$('.expense-row').map(row=>({name:$('[data-expense-name]',row).value,amount:$('[data-expense-amount]',row).value}));state.draft.expenses.splice(Number(btn.closest('.expense-row').dataset.index||0),1);renderWizardStep();});
}

async function submitWizard() {
  if(state.savingProduct)return;
  if(!captureStep())return;
  const payload={...state.draft}; delete payload.id; delete payload.result;
  state.savingProduct=true; $('#stepNext').disabled=true;
  try {
    const saved=state.editing?await api(`/api/products/${state.editing}`,{method:'PUT',body:payload}):(state.pendingSavedProduct||await api('/api/products',{method:'POST',body:payload}));
    if(!state.editing)state.pendingSavedProduct=saved;
    await api(`/api/products/${saved.id}/calculate`,{method:'POST',body:{product:saved,target_basis:saved.target_basis}});
    state.pendingSavedProduct=null; $('#wizardDialog').close(); await loadWorkspace(); showToast(t(state.editing?'updated':'saved')); state.activeProduct=saved.id;
  } catch(error) { showToast(error.message,'error'); }
  finally { state.savingProduct=false; $('#stepNext').disabled=false; }
}

async function quickCalculate(event) {
  event.preventDefault(); const form=new FormData(event.target?.id==='quickCalcForm'?event.target:event.currentTarget), payload=Object.fromEntries(form.entries()); payload.quantity=Number(payload.quantity); payload.expenses=[];
  try {
    const result=await api('/api/preview',{method:'POST',body:payload});
    if(result.history)state.history.unshift(result.history);
    $('#quickCalcResult').innerHTML=renderResultCard(result.result,payload.currency);
  } catch(error) { showToast(error.message,'error'); }
}
function renderResultCard(r,currency) {
  return `<div class="result-card"><div class="result-status">${statusPill(r)}</div><span class="result-eyebrow">${t(r.status==='loss'?'loss':'profit')}</span><strong class="result-amount ${profitClass(r)}">${moneyFmt(r.profit,currency)}</strong><span class="result-subtitle">${t('wholeProfit')}</span><div class="result-detail-grid"><div><span>${t('totalCost')}</span><strong>${moneyFmt(r.total_cost,currency)}</strong></div><div><span>${t('revenue')}</span><strong>${moneyFmt(r.revenue,currency)}</strong></div><div><span>${t('margin')}</span><strong>${r.margin_percent===null?'—':`${numberFmt(r.margin_percent)}%`}</strong></div><div><span>${t('breakEven')}</span><strong>${r.break_even_unit_price===null?'—':moneyFmt(r.break_even_unit_price,currency)}</strong></div><div><span>${t('targetPrice')} · ${escapeHtml(r.target_basis||'margin')}</span><strong>${r.target_percent_unit_price===null?'—':moneyFmt(r.target_percent_unit_price,currency)}</strong></div></div><p class="result-explain">${t('targetMeaning')}</p></div>`;
}

function openProduct(id,tab='info') {
  const product=state.products.find(p=>p.id===id); if(!product)return;
  if(state.activeProduct!==id)state.suggestions=null;state.aiReview=null;state.activeProduct=id; state.detailTab=tab; $('#detailTitle').textContent=product.name; $('#detailDialog').showModal(); renderDetailTab();
}
function renderDetailTab() {
  const p=state.products.find(item=>item.id===state.activeProduct); if(!p)return;
  $$('.detail-tab').forEach(tab=>tab.classList.toggle('active',tab.dataset.detailTab===state.detailTab));
  const body=$('#detailBody'), r=p.result||{}, c=p.currency;
  if(state.detailTab==='info') body.innerHTML=`<div class="detail-overview"><div class="detail-product-mark">${safeInitial(p.name)}</div><div><div class="eyebrow">${escapeHtml(p.category||t('products'))} · ${c}</div><h3>${escapeHtml(p.name)}</h3>${statusPill(r)}</div><div class="detail-price"><span>${t('finalPrice')}</span><strong>${moneyFmt(r.final_unit_price,c)}</strong></div></div><div class="detail-section"><h4>${t('purchaseDetails')}</h4><div class="detail-metric-grid"><div><span>${t('unitCost')}</span><strong>${moneyFmt(p.unit_cost,c)}</strong></div><div><span>${t('quantity')}</span><strong>${numberFmt(p.quantity)} ${t('unit')}</strong></div><div><span>${t('totalPurchase')}</span><strong>${moneyFmt(r.purchase_total,c)}</strong></div><div><span>${t('sellingPrice')}</span><strong>${moneyFmt(p.selling_price,c)}</strong></div></div></div><div class="detail-section"><h4>${t('pricingDetails')}</h4>${renderResultCard(r,c)}</div>`;
  else if(state.detailTab==='expenses') body.innerHTML=`<div class="detail-section"><div class="panel-head"><div><h3>${t('expenseBreakdown')}</h3><p>${t('expenseHelp')}</p></div><button class="button button-secondary" data-action="shared">⇄ ${state.lang==='ar'?'مصاريف مشتركة':'Shared expense'}</button></div><div class="expense-breakdown-row"><span>${t('totalPurchase')}</span><strong>${moneyFmt(r.purchase_total,c)}</strong></div>${(p.expenses||[]).map(e=>`<div class="expense-breakdown-row"><span>${escapeHtml(e.name)}</span><strong>${moneyFmt(e.amount,c)}</strong></div>`).join('')}${(p.shared_allocations||[]).map(e=>`<div class="expense-breakdown-row"><span>${escapeHtml(e.name)} <small class="basis-tag">${escapeHtml(e.basis)}</small></span><strong>${moneyFmt(e.amount,c)}</strong></div>`).join('')}<div class="expense-breakdown-row total"><span>${t('totalCost')}</span><strong>${moneyFmt(r.total_cost,c)}</strong></div><p class="quiet-note">${state.lang==='ar'?'لا يتم خصم التوصيل الذي يدفعه العميل.':'Customer-paid delivery is not deducted from profit.'}</p></div>`;
  else if(state.detailTab==='profit') body.innerHTML=`${renderResultCard(r,c)}<section class="detail-section"><h4>${t('pricingDetails')}</h4><div class="detail-metric-grid"><div><span>${t('profit')} / ${t('loss')}</span><strong class="${profitClass(r)}">${moneyFmt(r.profit,c)}</strong></div><div><span>${t('margin')}</span><strong>${r.margin_percent===null?'—':`${numberFmt(r.margin_percent)}%`}</strong></div><div><span>${t('breakEven')}</span><strong>${r.break_even_unit_price===null?'—':moneyFmt(r.break_even_unit_price,c)}</strong></div><div><span>${t('targetFixed')}</span><strong>${r.target_fixed_unit_price===null?'—':moneyFmt(r.target_fixed_unit_price,c)}</strong></div><div><span>${t('targetPercent')} · ${p.target_basis}</span><strong>${r.target_percent_unit_price===null?'—':moneyFmt(r.target_percent_unit_price,c)}</strong></div></div><button class="button button-secondary suggestion-button" id="suggestionButton">✦ ${t('suggestions')}</button>${state.suggestions?renderSuggestions(p):''}${state.aiAvailable?`<button class="button button-secondary suggestion-button" id="aiReviewButton">✦ ${t('aiReview')}</button>${state.aiReview?`<div class="suggestion-box"><p>${escapeHtml(state.aiReview)}</p><small>${t('aiDisclaimer')}</small></div>`:''}`:`<p class="quiet-note">${t('aiUnavailable')}</p>`}</section>`;
  else body.innerHTML=`<div class="scenarios-head"><div><h3>${t('scenarioCompare')}</h3><p>${t('targetMeaning')}</p></div><button class="button button-primary" id="newScenarioButton">＋ ${t('addScenario')}</button></div><div id="scenarioList" class="scenario-list"><div class="mini-empty">${t('loading')}</div></div>`;
  $('[data-action="shared"]',body)?.addEventListener('click',()=>openSharedDialog(p.id));
  $('#suggestionButton')?.addEventListener('click',()=>loadSuggestions(p));
  $('#aiReviewButton')?.addEventListener('click',()=>loadAiReview(p));
  $('#newScenarioButton')?.addEventListener('click',()=>openScenario(p));
  if(state.detailTab==='scenarios') loadScenarios(p);
}
function renderSuggestions(p) {
  if(state.suggestions==='loading')return `<div class="suggestion-box"><p>${t('loading')}</p></div>`;
  if(!state.suggestions?.available){const reason=state.suggestions?.reason_code==='price_already_high'?'suggestionAlreadyHigh':state.suggestions?.reason_code==='full_discount'?'suggestionNoBreakEven':null;return `<div class="suggestion-box"><h4>${t('suggestionsTitle')}</h4><p>${t(reason||'noSuggestions')}</p><small>${t('suggestionsLimit')}</small></div>`;}
  const advice=state.suggestions,c=p.currency;
  return `<div class="suggestion-box"><h4>${t('suggestionsTitle')}</h4><div class="suggestion-item"><span>↗</span><div><strong>${state.lang==='ar'?'قارن سعر البيع الأصلي المقترح':'Compare the suggested original selling price'}</strong><p>${moneyFmt(p.selling_price,c)} → ${moneyFmt(advice.suggested_price,c)} · ${t('discount')}: ${numberFmt(advice.discount_assumption)}%</p><small>${state.lang==='ar'?'الأثر الحسابي عند الكمية الحالية ':'Arithmetic impact at the current quantity '}${numberFmt(advice.quantity_assumption)}: ${moneyFmt(advice.profit_change,c)} ${t('profit').toLowerCase()}.</small><p>${t('totalCost')}: ${moneyFmt(advice.result.total_cost,c)} · ${t('profit')}: ${moneyFmt(advice.result.profit,c)}</p></div></div><small>${t('suggestionsLimit')}</small></div>`;
}
async function loadSuggestions(product) { state.suggestions='loading';renderDetailTab();try{state.suggestions=await api(`/api/products/${product.id}/suggestions`,{method:'POST',body:{}});renderDetailTab();}catch(e){state.suggestions=null;showToast(e.message,'error');renderDetailTab();} }
async function loadAiReview(product) { if(!confirm(t('aiConsent')))return;state.aiReview=t('loading');renderDetailTab();try{const data=await api(`/api/products/${product.id}/ai-review`,{method:'POST',body:{language:state.lang}});state.aiReview=data.review;}catch(e){state.aiReview=null;showToast(e.message,'error');}renderDetailTab(); }
async function loadScenarios(p) {
  try { const scenarios=await api(`/api/products/${p.id}/scenarios`); const box=$('#scenarioList'); if(!box)return; if(!scenarios.length){box.innerHTML=`<div class="mini-empty">${t('noScenarios')}</div>`;return;} box.innerHTML=`<div class="scenario-table-head"><span>${t('scenario')}</span><span>${t('price')}</span><span>${t('discountShort')}</span><span>${t('finalUnit')}</span><span>${t('wholeProfit')}</span><span></span></div>${scenarios.map(s=>`<div class="scenario-row"><strong>${escapeHtml(s.name)}</strong><span>${moneyFmt(s.selling_price,p.currency)}</span><span>${numberFmt(s.discount_percent)}%</span><span>${moneyFmt(s.result.final_unit_price,p.currency)}</span><strong class="${profitClass(s.result)}">${moneyFmt(s.result.profit,p.currency)}</strong><div class="scenario-actions"><button class="row-open" data-edit-scenario="${s.id}" aria-label="${t('edit')}">✎</button><button class="row-open" data-delete-scenario="${s.id}" aria-label="${t('delete')}">×</button></div></div>`).join('')}`; $$('[data-edit-scenario]',box).forEach(b=>b.onclick=()=>openScenario(p,scenarios.find(s=>s.id===b.dataset.editScenario))); $$('[data-delete-scenario]',box).forEach(b=>b.onclick=async()=>{if(!confirm(t('deleteConfirm')))return;try{await api(`/api/scenarios/${b.dataset.deleteScenario}`,{method:'DELETE'});loadScenarios(p);showToast(t('deleted'));}catch(e){showToast(e.message,'error');}}); } catch(e) { showToast(e.message,'error'); }
}
function openScenario(p, scenario=null) { const form=$('#scenarioForm'); form.reset(); form.dataset.productId=p.id; if(scenario)form.dataset.scenarioId=scenario.id;else delete form.dataset.scenarioId; $('#scenarioTitle').textContent=t(scenario?'editScenario':'newScenario'); form.elements.name.value=scenario?.name||''; form.elements.selling_price.value=scenario?.selling_price??p.selling_price; form.elements.discount_percent.value=scenario?.discount_percent??0; $('#scenarioDialog').showModal(); }

function openAuth(mode='signup') { state.authMode=mode; $('#authTitle').textContent=t(mode==='signup'?'createAccount':'signIn'); $('.migration-choice').hidden=mode!=='signup'; if($('#forgotPasswordToggle'))$('#forgotPasswordToggle').hidden=mode==='signup'; $('#authForm [name="password"]').minLength=mode==='signup'?12:1; $('#authForm [name="password"]').autocomplete=mode==='signup'?'new-password':'current-password'; $('#authModeToggle').textContent=t(mode==='signup'?'haveAccount':'noAccount'); $('#authDialog').showModal(); }
async function authSubmit(event) { event.preventDefault(); const fd=new FormData(event.currentTarget), mode=state.authMode; const path=mode==='signup'?'/api/auth/signup':'/api/auth/login'; const body={email:fd.get('email'),password:fd.get('password'),transfer_guest:fd.get('transfer_guest')==='true'};try{state.session=await api(path,{method:'POST',body});$('#authDialog').close();await loadWorkspace();showToast(mode==='signup'?t('createAccount'):t('signIn'));}catch(e){showToast(e.message,'error');} }
async function logout() { try{state.session=await api('/api/session',{method:'POST',body:{action:'logout'}});state.csrf=state.session.csrf;await loadWorkspace();showToast(t('logout'));}catch(e){showToast(e.message,'error');} }

function setupVoice() {
  const Recognition=window.SpeechRecognition||window.webkitSpeechRecognition;
  if(!Recognition){$('#voiceStatus').textContent=t('unsupportedVoice');return;}
  const button=$('#voiceButton'), status=$('#voiceStatus');
  const restoreButton=()=>{button.classList.remove('recording');button.setAttribute('aria-pressed','false');button.innerHTML=`<span>&bull;</span><span>${t('voiceStart')}</span>`;};
  if(state.recording||state.voiceStarting){
    state.voiceStopping=true;status.textContent=t('stoppingVoice');
    try{state.recognition.stop();}catch{state.voiceErrorMessage=t('voiceError');state.recording=false;state.voiceStarting=false;restoreButton();status.textContent=state.voiceErrorMessage;}
    return;
  }
  const recognition=new Recognition();
  state.recognition=recognition;state.voiceStarting=true;state.recording=true;state.voiceStopping=false;state.voiceAbort=false;state.voiceTranscript='';state.voiceErrorMessage='';
  recognition.lang=state.lang==='ar'?'ar':'en-US';recognition.continuous=true;recognition.interimResults=true;recognition.maxAlternatives=1;
  button.classList.add('recording');button.setAttribute('aria-pressed','true');button.innerHTML=`<span class="record-pulse">●</span><span>${t('voiceStop')}</span>`;status.textContent=t('recording');
  recognition.onstart=()=>{state.voiceStarting=false;};
  recognition.onresult=()=>{
    let finalText='',interimText='';
    for(let i=0;i<recognition.results.length;i++){const result=recognition.results[i];if(result.isFinal)finalText+=result[0].transcript+' ';else interimText+=result[0].transcript+' ';}
    state.voiceTranscript=finalText.trim();if(state.voiceTranscript)populateVoice(state.voiceTranscript);
    status.textContent=state.voiceTranscript?`${t('transcribed')} “${state.voiceTranscript}”`:interimText?`${t('recording')} ${interimText.trim()}`:t('recording');
  };
  recognition.onerror=event=>{
    const errors={'not-allowed':'permissionVoice','service-not-allowed':'permissionVoice','no-speech':'noSpeechVoice',network:'networkVoice','audio-capture':'microphoneVoice'};
    state.voiceErrorMessage=t(errors[event.error]||'voiceError');state.recording=false;state.voiceStarting=false;restoreButton();status.textContent=state.voiceErrorMessage;
  };
  recognition.onend=()=>{
    const showStatus=!state.voiceAbort;const message=state.voiceErrorMessage||(state.voiceTranscript?t('transcribed'):state.voiceStopping?t('stoppedVoice'):t('voiceError'));
    state.recording=false;state.voiceStarting=false;state.voiceStopping=false;state.recognition=null;restoreButton();if(showStatus)status.textContent=message;
  };
  try{recognition.start();}catch{state.recording=false;state.voiceStarting=false;state.voiceErrorMessage=t('voiceError');state.recognition=null;restoreButton();status.textContent=state.voiceErrorMessage;}
}
function populateVoice(text) {
  // Extract only explicit numeric values; never infer missing values.
  const normalized=text.replace(/[٠-٩]/g,d=>'٠١٢٣٤٥٦٧٨٩'.indexOf(d)).replace(/[٫٬]/g,'.');
  const entries=[
    ['quantity',/(?:(\d+)\s*(?:units?|pieces?|قطع|قطعة|حبة|عدد)|(?:quantity|units?|pieces?|قطع|قطعة|حبة|عدد)\D{0,12}(\d+))/i],
    ['unit_cost',/(?:(\d+(?:\.\d+)?)\s*(?:per\s*(?:unit|piece)|لل(?:قطعة|حبة|وحدة))|(?:unit\s*(?:cost|price)|per\s*(?:unit|piece)|سعر\s*(?:القطعة|الحبة)|تكلفة\s*(?:القطعة|الوحدة))\D{0,16}(\d+(?:\.\d+)?))/i],
    ['selling_price',/(?:selling\s*price|sell\s*(?:for|at)|سعر\s*البيع|(?:ابيع|نبيع|نبيعه|أبيعه)\s*بـ?)\D{0,16}(\d+(?:\.\d+)?)/i],
    ['discount_percent',/(?:(\d+(?:\.\d+)?)\s*%\s*(?:discount|خصم)|(?:discount|خصم)\D{0,12}(\d+(?:\.\d+)?)\s*%?)/i],
  ];
  for(const [key,regex] of entries){
    const match=normalized.match(regex);
    if(match){
      const val=match[1]||match[2];
      if(val!==undefined){
        state.draft[key]=val;
        const field=$(`#wizardBody [name="${key}"]`);
        if(field){field.value=val;field.classList.add('voice-populated');}
      }
    }
  }
  const currency=/(?:shekel|ils|شيكل)/i.test(text)?'ILS':/(?:dinar|jod|دينار)/i.test(text)?'JOD':/(?:dollar|usd|دولار)/i.test(text)?'USD':/(?:euro|eur|يورو)/i.test(text)?'EUR':/(?:pound|gbp|جنيه\s*استرليني|باوند)/i.test(text)?'GBP':/(?:riyal|sar|ريال)/i.test(text)?'SAR':/(?:dirham|aed|درهم)/i.test(text)?'AED':/(?:egp|جنيه\s*مصري|جنيه)/i.test(text)?'EGP':null;
  if(currency){state.draft.currency=currency;const field=$('#wizardBody [name="currency"]');if(field)field.value=currency;}
  const nameMatch=text.match(/(?:product|منتج)\s*[:：]?\s*([\p{L}\s]{2,30})/iu);if(nameMatch){state.draft.name=nameMatch[1].trim();const field=$('#wizardBody [name="name"]');if(field)field.value=state.draft.name;}
}

async function openSharedDialog(productId) {
  const selected=state.products.find(p=>p.id===productId); const products=selected?state.products.filter(p=>p.currency===selected.currency):state.products;
  const existing=await api('/api/shared-expenses').catch(()=>[]);
  const matchingExpenses=existing.filter(e=>!selected||e.product_ids.some(id=>state.products.find(p=>p.id===id)?.currency===selected.currency));
  $('#sharedProductList').innerHTML=`<div class="shared-select-label">${state.lang==='ar'?'وزّع على المنتجات':'Apply to products'} · ${products[0]?.currency||''}</div>${products.map(p=>`<label class="shared-product-option"><input type="checkbox" name="product_ids" value="${p.id}" data-currency="${p.currency}" ${p.id===productId?'checked':''}><span><strong>${escapeHtml(p.name)}</strong><small>${p.currency} · ${numberFmt(p.quantity)} ${t('unit')}</small></span></label>`).join('')}${matchingExpenses.length?`<div class="shared-existing-title">${state.lang==='ar'?'المصاريف المشتركة المحفوظة':'Saved shared expenses'}</div>${matchingExpenses.map(e=>{const currency=state.products.find(p=>e.product_ids.includes(p.id))?.currency||'USD';return `<div class="shared-existing"><span>${escapeHtml(e.name)} · ${moneyFmt(e.amount,currency)} <small>${e.basis}</small></span><button type="button" data-remove-shared="${e.id}" aria-label="${t('delete')}">×</button></div>`;}).join('')}`:''}`;
  $$('[data-remove-shared]').forEach(button=>button.onclick=async()=>{if(!confirm(state.lang==='ar'?'حذف المصروف المشترك سيحذفه من جميع المنتجات المشاركة. هل تريد المتابعة؟':'Delete this shared expense from every selected product?'))return;try{await api(`/api/shared-expenses/${button.dataset.removeShared}`,{method:'DELETE'});$('#sharedDialog').close();await loadWorkspace();openSharedDialog(productId);}catch(e){showToast(e.message,'error');}});
  const form=$('#sharedForm'); form.dataset.currency=products[0]?.currency||'USD'; if(selected)form.dataset.productId=productId; else delete form.dataset.productId; form.reset();
  const basis=form.elements.basis; basis.innerHTML=`<option value="quantity">${state.lang==='ar'?'حسب الكمية':'By quantity'}</option><option value="purchase_value" ${products.every(p=>Number(p.unit_cost)*Number(p.quantity)>0)?'':'disabled'}>${state.lang==='ar'?'حسب قيمة الشراء':'By purchase value'}</option><option value="weight" ${products.every(p=>Number(p.weight)>0)?'':'disabled'}>${state.lang==='ar'?'حسب الوزن':'By weight'}</option>`;
  $$('#sharedProductList input[name="product_ids"]').forEach(box=>box.onchange=()=>{const picked=$$('#sharedProductList input[name="product_ids"]:checked');const currency=picked[0]?.dataset.currency;$$('#sharedProductList input[name="product_ids"]').forEach(item=>{item.disabled=!!currency&&item.dataset.currency!==currency;});const selectedProducts=state.products.filter(p=>picked.some(item=>item.value===p.id));basis.querySelector('[value="purchase_value"]').disabled=selectedProducts.length>0&&!selectedProducts.every(p=>Number(p.unit_cost)*Number(p.quantity)>0);basis.querySelector('[value="weight"]').disabled=selectedProducts.length>0&&!selectedProducts.every(p=>Number(p.weight)>0);});
  $('#sharedDialog').showModal();
}

function setup() {
  const page=$('#pageContent');
  const saveQuickDraft=event=>{if(event.target.closest('#quickCalcForm'))state.quickDraft=Object.fromEntries(new FormData(event.target.form||event.target.closest('form')).entries());};
  page.addEventListener('input',saveQuickDraft); page.addEventListener('change',saveQuickDraft);
  $('#languageToggle').onclick=()=>{state.lang=state.lang==='en'?'ar':'en';setLocale();}; $('#themeToggle').onclick=()=>{state.theme=state.theme==='light'?'dark':'light';setLocale();};
  $('#mobileMenu').setAttribute('aria-expanded',String(!matchMedia('(max-width: 850px)').matches)); $('#mobileMenu').onclick=()=>{const sidebar=$('#sidebar');if(matchMedia('(max-width: 850px)').matches){sidebar.classList.add('sidebar-open');$('#scrim').classList.add('visible');$('#mobileMenu').setAttribute('aria-expanded','true');}else{document.querySelector('.app-frame').classList.toggle('sidebar-collapsed');$('#mobileMenu').setAttribute('aria-expanded',String(!document.querySelector('.app-frame').classList.contains('sidebar-collapsed')));}}; $('#scrim').onclick=()=>{$('#sidebar').classList.remove('sidebar-open');$('#scrim').classList.remove('visible');$('#mobileMenu').setAttribute('aria-expanded','false');};
  $$('.nav-item[data-route]').forEach(b=>b.onclick=()=>navigate(b.dataset.route)); $('#searchInput').addEventListener('input',e=>{state.search=e.target.value;if(state.route!=='products'&&state.search.trim())state.route='products';renderPage();});
  $('#profileButton').onclick=$('#topProfile').onclick=()=>state.session?.profile?navigate('settings'):openAuth('signup'); $('#notificationButton').onclick=()=>showToast(t('noActivity'),'info');
  $$('.close-dialog').forEach(b=>b.addEventListener('click',()=>b.closest('dialog').close()));
  $$('dialog').forEach(d=>d.addEventListener('click',e=>{if(e.target===d)d.close();}));
  $('#productForm').addEventListener('submit',event=>{event.preventDefault();if(state.step<3){if(captureStep()){state.step++;renderWizardStep();}}else submitWizard();});
  $('#stepBack').onclick=()=>{captureStep();state.step=Math.max(0,state.step-1);renderWizardStep();}; $('#stepNext').onclick=()=>state.step<3?(captureStep()&&(state.step++,renderWizardStep())):submitWizard();
  $('#voiceButton').onclick=setupVoice; $('#editProductButton').onclick=()=>{const p=state.products.find(x=>x.id===state.activeProduct);$('#detailDialog').close();openWizard(p);};
  $('#deleteProductButton').onclick=async()=>{const p=state.products.find(item=>item.id===state.activeProduct);if(!p||!confirm(t('confirmDelete')))return;try{await api(`/api/products/${p.id}`,{method:'DELETE'});$('#detailDialog').close();await loadWorkspace();showToast(t('deleted'));}catch(e){showToast(e.message,'error');}};
  $$('.detail-tab').forEach(b=>b.onclick=()=>{state.detailTab=b.dataset.detailTab;renderDetailTab();});
  $('#scenarioForm').onsubmit=async event=>{event.preventDefault();const form=event.currentTarget,fd=new FormData(form);try{const id=form.dataset.scenarioId;await api(id?`/api/scenarios/${id}`:`/api/products/${form.dataset.productId}/scenarios`,{method:id?'PUT':'POST',body:Object.fromEntries(fd.entries())});$('#scenarioDialog').close();renderDetailTab();showToast(t('scenarioSaved'));}catch(e){showToast(e.message,'error');}};
  $('#authForm').onsubmit=authSubmit; $('#authModeToggle').onclick=()=>openAuth(state.authMode==='signup'?'login':'signup'); if($('#forgotPasswordToggle'))$('#forgotPasswordToggle').onclick=()=>{ $('#authDialog').close(); $('#resetForm').reset(); $('#resetDialog').showModal(); }; if($('#resetForm'))$('#resetForm').onsubmit=async event=>{ event.preventDefault(); const fd=new FormData(event.currentTarget); try { await api('/api/auth/request-password-reset', { method:'POST', body:{ email:fd.get('email') } }); $('#resetDialog').close(); showToast(t('resetSent')); } catch(e) { showToast(e.message, 'error'); } }; $('#googleSignInButton').onclick=()=>{const transfer=state.authMode==='signup'&&$('input[name="transfer_guest"]:checked')?.value==='true';location.assign(`/auth/google/start?transfer_guest=${transfer}`);};
  $('#sharedForm').onsubmit=async event=>{event.preventDefault();const fd=new FormData(event.currentTarget);const ids=fd.getAll('product_ids');try{await api('/api/shared-expenses',{method:'POST',body:{name:fd.get('name'),amount:fd.get('amount'),basis:fd.get('basis'),product_ids:ids}});$('#sharedDialog').close();await loadWorkspace();const active=state.products.find(p=>p.id===state.activeProduct);if(active&&$('#detailDialog').open){$('#detailTitle').textContent=active.name;state.detailTab='expenses';renderDetailTab();}showToast(t('saved'));}catch(e){showToast(e.message,'error');}};
  $('#voiceButton').setAttribute('aria-pressed','false'); $('#wizardDialog').addEventListener('close',()=>{if(state.recording||state.voiceStarting){state.voiceAbort=true;try{state.recognition?.abort();}catch{}state.recording=false;state.voiceStarting=false;state.voiceStopping=false;state.recognition=null;$('#voiceButton').classList.remove('recording');$('#voiceButton').setAttribute('aria-pressed','false');$('#voiceButton').innerHTML=`<span>&bull;</span><span>${t('voiceStart')}</span>`;}});
  setLocale();
}

(async()=>{setup();try{state.session=await api('/api/session');state.csrf=state.session.csrf;state.aiAvailable=(await api('/api/ai/status')).available;await loadWorkspace();const params=new URLSearchParams(location.search);if(params.has('auth_success'))showToast(t('signIn'));else if(params.get('auth_error'))showToast(t(params.get('auth_error')==='google_unavailable'?'googleUnavailable':params.get('auth_error')==='google_cancelled'?'googleCancelled':'googleFailed'),'error');if(params.has('auth_success')||params.has('auth_error'))history.replaceState(null,'',location.pathname+location.hash);}catch(error){$('#pageContent').innerHTML=`<div class="empty-products"><h2>${t('error')}</h2><p>${escapeHtml(error.message)}</p><button class="button button-primary" onclick="location.reload()">↻ ${t('continue')}</button></div>`;}})();
