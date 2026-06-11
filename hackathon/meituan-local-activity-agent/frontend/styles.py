"""美团暖色生活风 CSS 设计系统"""

import streamlit as st


def inject_css():
    """注入全局 CSS。在 app.py 顶部调用一次。"""

    css = """"
    /* ============================================
       CSS Custom Properties — Design Tokens
       ============================================ */
    :root {
        /* Primary: 美团暖黄 */
        --primary-50:  #FFF9E6;
        --primary-100: #FFF0BF;
        --primary-200: #FFE699;
        --primary-300: #FFD966;
        --primary-400: #FFC833;
        --primary-500: #FFB800;
        --primary-600: #E5A500;
        --primary-700: #B38200;

        /* Warm-tinted neutrals */
        --gray-50:  #FAFAF8;
        --gray-100: #F5F4F0;
        --gray-200: #E8E6E0;
        --gray-300: #D4D1C8;
        --gray-400: #A9A59A;
        --gray-500: #7D7870;
        --gray-600: #5C5850;
        --gray-700: #3D3A34;
        --gray-800: #2A2824;
        --gray-900: #1A1916;

        /* Semantic */
        --success:     #16A34A;
        --success-bg:  #F0FDF4;
        --success-border: #BBF7D0;
        --error:       #DC2626;
        --error-bg:    #FEF2F2;
        --error-border:#FECACA;
        --warning:     #D97706;
        --warning-bg:  #FFFBEB;
        --warning-border:#FDE68A;
        --info:        #2563EB;
        --info-bg:     #EFF6FF;

        /* Score colors */
        --score-high:  #16A34A;
        --score-mid:   #D97706;
        --score-low:   #DC2626;

        /* Elevation */
        --shadow-xs:  0 1px 2px rgba(26, 25, 22, 0.04);
        --shadow-sm:  0 1px 3px rgba(26, 25, 22, 0.05), 0 1px 2px rgba(26, 25, 22, 0.03);
        --shadow-md:  0 4px 12px rgba(26, 25, 22, 0.06), 0 2px 4px rgba(26, 25, 22, 0.03);
        --shadow-lg:  0 8px 24px rgba(26, 25, 22, 0.08), 0 4px 8px rgba(26, 25, 22, 0.04);
        --shadow-xl:  0 16px 48px rgba(26, 25, 22, 0.10), 0 8px 16px rgba(26, 25, 22, 0.05);

        /* Radius */
        --radius-sm:  8px;
        --radius-md:  12px;
        --radius-lg:  16px;
        --radius-xl:  24px;

        /* Motion */
        --ease-out:   cubic-bezier(0.25, 1, 0.5, 1);
        --ease-out-fast: cubic-bezier(0.22, 1, 0.36, 1);
        --duration-fast: 150ms;
        --duration-normal: 250ms;
        --duration-slow: 400ms;
    }

    /* ============================================
       Base Reset & Streamlit Overrides
       ============================================ */

    /* Hide default header */
    header[data-testid="stHeader"] {
        background: transparent !important;
        padding: 0 !important;
    }
    [data-testid="stHeader"]::before {
        display: none !important;
    }

    /* Hide hamburger menu and sidebar */
    button[kind="header"],
    [data-testid="stSidebarCollapsedControl"],
    section[data-testid="stSidebar"] {
        display: none !important;
    }

    /* Main container */
    .main .block-container {
        max-width: 960px !important;
        padding-top: 2rem !important;
        padding-bottom: 4rem !important;
    }

    /* Body background */
    .stApp {
        background: var(--gray-50) !important;
    }

    /* Typography base */
    .stMarkdown, p, span, div {
        font-family: -apple-system, BlinkMacSystemFont, "PingFang SC",
                     "Hiragino Sans GB", "Microsoft YaHei", "Noto Sans SC",
                     sans-serif !important;
        color: var(--gray-700);
        line-height: 1.6;
    }

    /* ============================================
       Hero Section
       ============================================ */
    .hero {
        text-align: center;
        padding: 3rem 0 2rem;
    }
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: var(--primary-50);
        border: 1px solid var(--primary-200);
        color: var(--primary-700);
        padding: 6px 16px;
        border-radius: 100px;
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.03em;
        margin-bottom: 1.25rem;
    }
    .hero h1 {
        font-size: clamp(1.75rem, 4vw, 2.5rem) !important;
        font-weight: 800 !important;
        color: var(--gray-900) !important;
        letter-spacing: -0.03em !important;
        line-height: 1.2 !important;
        margin: 0 0 0.75rem !important;
    }
    .hero p {
        font-size: 1.05rem !important;
        color: var(--gray-500) !important;
        max-width: 480px;
        margin: 0 auto !important;
        line-height: 1.7 !important;
    }

    /* ============================================
       Input Section
       ============================================ */
    .input-section {
        background: white;
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-md);
        padding: 1.75rem;
        margin-bottom: 2rem;
        border: 1px solid var(--gray-200);
        transition: box-shadow var(--duration-normal) var(--ease-out);
    }
    .input-section:focus-within {
        box-shadow: var(--shadow-lg);
        border-color: var(--primary-300);
    }
    .input-label {
        font-size: 0.85rem;
        font-weight: 600;
        color: var(--gray-600);
        margin-bottom: 0.75rem;
        display: block;
    }

    /* Override Streamlit textarea */
    .input-section [data-testid="stTextArea"] {
        border: none !important;
    }
    .input-section [data-testid="stTextArea"] textarea {
        border: 1.5px solid var(--gray-200) !important;
        border-radius: var(--radius-md) !important;
        padding: 14px 16px !important;
        font-size: 0.95rem !important;
        color: var(--gray-800) !important;
        background: var(--gray-50) !important;
        transition: border-color var(--duration-fast) var(--ease-out),
                    box-shadow var(--duration-fast) var(--ease-out) !important;
        min-height: 80px !important;
        line-height: 1.6 !important;
    }
    .input-section [data-testid="stTextArea"] textarea:focus {
        border-color: var(--primary-400) !important;
        box-shadow: 0 0 0 3px rgba(255, 184, 0, 0.12) !important;
        background: white !important;
    }
    .input-section [data-testid="stTextArea"] textarea::placeholder {
        color: var(--gray-400) !important;
    }

    /* Submit button */
    .submit-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        width: 100%;
        margin-top: 1rem;
        padding: 14px 24px;
        background: linear-gradient(135deg, var(--primary-500) 0%, var(--primary-600) 100%);
        color: white !important;
        border: none;
        border-radius: var(--radius-md);
        font-size: 0.95rem;
        font-weight: 600;
        cursor: pointer;
        transition: transform var(--duration-fast) var(--ease-out),
                    box-shadow var(--duration-fast) var(--ease-out);
        box-shadow: 0 2px 8px rgba(255, 184, 0, 0.25);
    }
    .submit-btn:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 16px rgba(255, 184, 0, 0.35);
    }
    .submit-btn:active {
        transform: translateY(0);
    }

    /* Hide default Streamlit button (we use custom HTML button) */
    .hide-st-btn [data-testid="stBaseButton-primary"],
    .hide-st-btn [data-testid="stFormSubmitButton"] {
        display: none !important;
    }

    /* ============================================
       Section Headers
       ============================================ */
    .section-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 1.25rem;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid var(--gray-100);
    }
    .section-header .section-icon {
        width: 36px;
        height: 36px;
        border-radius: var(--radius-sm);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
        flex-shrink: 0;
    }
    .section-header h2 {
        font-size: 1.15rem !important;
        font-weight: 700 !important;
        color: var(--gray-900) !important;
        margin: 0 !important;
        letter-spacing: -0.01em !important;
    }
    .section-header .section-sub {
        font-size: 0.8rem;
        color: var(--gray-400);
        margin-left: auto;
    }

    /* ============================================
       Intent Card
       ============================================ */
    .intent-card {
        background: white;
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-sm);
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border: 1px solid var(--gray-200);
    }
    .intent-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
        gap: 1rem;
    }
    .intent-item {
        display: flex;
        flex-direction: column;
        gap: 4px;
    }
    .intent-label {
        font-size: 0.75rem;
        font-weight: 600;
        color: var(--gray-400);
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    .intent-value {
        font-size: 0.95rem;
        font-weight: 600;
        color: var(--gray-800);
    }
    .intent-missing {
        background: var(--warning-bg);
        border: 1px solid var(--warning-border);
        border-radius: var(--radius-sm);
        padding: 10px 14px;
        margin-top: 1rem;
        font-size: 0.85rem;
        color: var(--warning);
    }

    /* ============================================
       Plan Cards
       ============================================ */
    .plans-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 1rem;
        margin-bottom: 1.5rem;
    }
    .plan-card {
        background: white;
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-sm);
        padding: 1.5rem;
        border: 1.5px solid var(--gray-200);
        transition: box-shadow var(--duration-normal) var(--ease-out),
                    border-color var(--duration-normal) var(--ease-out),
                    transform var(--duration-fast) var(--ease-out);
        position: relative;
        overflow: hidden;
    }
    .plan-card:hover {
        box-shadow: var(--shadow-md);
        border-color: var(--gray-300);
        transform: translateY(-2px);
    }
    .plan-card.is-best {
        border-color: var(--primary-400);
        box-shadow: var(--shadow-md), 0 0 0 1px var(--primary-100);
    }
    .plan-card.is-best::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--primary-400), var(--primary-600));
    }
    .plan-badge {
        display: inline-flex;
        align-items: center;
        padding: 3px 10px;
        border-radius: 100px;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }
    .plan-badge-badge {
        background: var(--gray-100);
        color: var(--gray-600);
    }
    .plan-badge-winner {
        background: var(--primary-100);
        color: var(--primary-700);
    }
    .plan-name {
        font-size: 1.05rem !important;
        font-weight: 700 !important;
        color: var(--gray-900) !important;
        margin: 0.75rem 0 0.5rem !important;
        line-height: 1.4 !important;
    }
    .plan-desc {
        font-size: 0.85rem !important;
        color: var(--gray-500) !important;
        margin-bottom: 1rem !important;
        line-height: 1.6 !important;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
    .plan-metrics {
        display: flex;
        gap: 1.25rem;
        margin-bottom: 1rem;
        padding: 0.75rem 0;
        border-top: 1px solid var(--gray-100);
        border-bottom: 1px solid var(--gray-100);
    }
    .plan-metric {
        display: flex;
        flex-direction: column;
        gap: 2px;
    }
    .plan-metric-value {
        font-size: 1.1rem;
        font-weight: 700;
        color: var(--gray-800);
    }
    .plan-metric-label {
        font-size: 0.7rem;
        font-weight: 500;
        color: var(--gray-400);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .plan-highlights {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
    }
    .highlight-tag {
        display: inline-flex;
        align-items: center;
        padding: 4px 10px;
        background: var(--gray-50);
        border: 1px solid var(--gray-200);
        border-radius: 100px;
        font-size: 0.75rem;
        color: var(--gray-600);
        font-weight: 500;
    }

    /* POI timeline within plan */
    .poi-timeline {
        margin-top: 1rem;
        padding-top: 0.75rem;
        border-top: 1px solid var(--gray-100);
    }
    .poi-item {
        display: flex;
        gap: 10px;
        padding: 8px 0;
        position: relative;
    }
    .poi-item:not(:last-child)::after {
        content: "";
        position: absolute;
        left: 11px;
        top: 32px;
        bottom: -8px;
        width: 1.5px;
        background: var(--gray-200);
    }
    .poi-dot {
        width: 24px;
        height: 24px;
        border-radius: 50%;
        background: var(--primary-50);
        border: 2px solid var(--primary-300);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.65rem;
        flex-shrink: 0;
        color: var(--primary-600);
        margin-top: 2px;
    }
    .poi-info {
        flex: 1;
        min-width: 0;
    }
    .poi-name {
        font-size: 0.85rem;
        font-weight: 600;
        color: var(--gray-800);
    }
    .poi-meta {
        font-size: 0.75rem;
        color: var(--gray-400);
        margin-top: 2px;
    }

    /* ============================================
       Score Matrix
       ============================================ */
    .score-card {
        background: white;
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-sm);
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border: 1px solid var(--gray-200);
        overflow-x: auto;
    }
    .score-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        font-size: 0.85rem;
    }
    .score-table thead th {
        padding: 10px 14px;
        text-align: left;
        font-weight: 600;
        color: var(--gray-500);
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        border-bottom: 2px solid var(--gray-200);
        white-space: nowrap;
    }
    .score-table thead th:first-child {
        border-radius: var(--radius-sm) 0 0 0;
    }
    .score-table thead th:last-child {
        border-radius: 0 var(--radius-sm) 0 0;
    }
    .score-table tbody td {
        padding: 10px 14px;
        border-bottom: 1px solid var(--gray-100);
        color: var(--gray-700);
        vertical-align: middle;
    }
    .score-table tbody tr:last-child td {
        border-bottom: none;
    }
    .score-table .agent-name {
        font-weight: 600;
        color: var(--gray-800);
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .score-table .agent-weight {
        font-size: 0.7rem;
        color: var(--gray-400);
        font-weight: 400;
    }
    .score-cell {
        font-weight: 700;
        font-size: 0.95rem;
        text-align: center;
        padding: 8px 14px !important;
    }
    .score-high {
        color: var(--score-high);
        background: var(--success-bg);
        border-radius: 6px;
    }
    .score-mid {
        color: var(--score-mid);
        background: var(--warning-bg);
        border-radius: 6px;
    }
    .score-low {
        color: var(--score-low);
        background: var(--error-bg);
        border-radius: 6px;
    }
    .score-veto {
        color: white !important;
        background: var(--error) !important;
        border-radius: 6px;
        font-size: 0.7rem;
        padding: 4px 10px !important;
    }
    .score-table .final-row td {
        font-weight: 700;
        background: var(--primary-50);
        border-top: 2px solid var(--primary-200);
    }
    .score-table .final-score {
        color: var(--primary-700);
        font-size: 1rem;
    }

    /* ============================================
       Best Plan Section
       ============================================ */
    .best-plan-card {
        background: linear-gradient(135deg, var(--primary-50) 0%, white 100%);
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-md);
        padding: 2rem;
        margin-bottom: 1.5rem;
        border: 1.5px solid var(--primary-200);
        position: relative;
        overflow: hidden;
    }
    .best-plan-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--primary-400), var(--primary-600), var(--primary-400));
    }
    .best-plan-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 1.25rem;
    }
    .best-plan-icon {
        width: 48px;
        height: 48px;
        border-radius: var(--radius-md);
        background: linear-gradient(135deg, var(--primary-400), var(--primary-600));
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        box-shadow: 0 4px 12px rgba(255, 184, 0, 0.3);
    }
    .best-plan-title {
        flex: 1;
    }
    .best-plan-title h2 {
        font-size: 1.25rem !important;
        font-weight: 700 !important;
        color: var(--gray-900) !important;
        margin: 0 !important;
    }
    .best-plan-title .score-display {
        font-size: 0.85rem;
        color: var(--gray-500);
        margin-top: 2px;
    }
    .best-plan-score-badge {
        background: linear-gradient(135deg, var(--primary-500), var(--primary-700));
        color: white;
        padding: 8px 16px;
        border-radius: var(--radius-sm);
        font-size: 1.25rem;
        font-weight: 800;
        box-shadow: 0 2px 8px rgba(255, 184, 0, 0.3);
    }

    /* Execution results */
    .exec-results {
        margin-top: 1.25rem;
        padding-top: 1rem;
        border-top: 1px solid var(--primary-200);
    }
    .exec-item {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 6px 0;
        font-size: 0.85rem;
    }
    .exec-icon {
        width: 20px;
        height: 20px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.65rem;
        flex-shrink: 0;
    }
    .exec-icon-success {
        background: var(--success-bg);
        color: var(--success);
        border: 1px solid var(--success-border);
    }
    .exec-icon-fail {
        background: var(--error-bg);
        color: var(--error);
        border: 1px solid var(--error-border);
    }

    /* ============================================
       Loading State
       ============================================ */
    .loader-container {
        text-align: center;
        padding: 3rem 1rem;
    }
    .loader-pulse {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        background: linear-gradient(135deg, var(--primary-400), var(--primary-600));
        margin: 0 auto 1.5rem;
        animation: loaderPulse 1.5s ease-in-out infinite;
    }
    .loader-text {
        font-size: 1rem;
        font-weight: 600;
        color: var(--gray-700);
        margin-bottom: 0.5rem;
    }
    .loader-sub {
        font-size: 0.85rem;
        color: var(--gray-400);
    }
    .loader-steps {
        margin-top: 1.5rem;
        text-align: left;
        max-width: 320px;
        margin-left: auto;
        margin-right: auto;
    }
    .loader-step {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 8px 0;
        font-size: 0.85rem;
        color: var(--gray-400);
        transition: color var(--duration-normal) var(--ease-out);
    }
    .loader-step.active {
        color: var(--gray-700);
        font-weight: 500;
    }
    .loader-step.done {
        color: var(--success);
    }
    .loader-step-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--gray-300);
        flex-shrink: 0;
        transition: background var(--duration-normal) var(--ease-out);
    }
    .loader-step.active .loader-step-dot {
        background: var(--primary-500);
        animation: dotPulse 1s ease-in-out infinite;
    }
    .loader-step.done .loader-step-dot {
        background: var(--success);
    }

    /* ============================================
       Error State
       ============================================ */
    .error-card {
        background: var(--error-bg);
        border: 1px solid var(--error-border);
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }
    .error-card h3 {
        color: var(--error) !important;
        font-size: 1rem !important;
        margin: 0 0 0.5rem !important;
    }
    .error-card p {
        color: var(--gray-600) !important;
        font-size: 0.9rem !important;
        margin: 0 !important;
    }

    /* ============================================
       Trace Footer
       ============================================ */
    .trace-footer {
        text-align: center;
        padding: 1.5rem 0;
        font-size: 0.75rem;
        color: var(--gray-400);
    }
    .trace-footer code {
        background: var(--gray-100);
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.7rem;
        color: var(--gray-500);
    }

    /* ============================================
       Utility Classes
       ============================================ */
    .mb-sm { margin-bottom: 0.5rem; }
    .mb-md { margin-bottom: 1rem; }
    .mb-lg { margin-bottom: 1.5rem; }
    .mb-xl { margin-bottom: 2rem; }
    .mt-sm { margin-top: 0.5rem; }
    .mt-md { margin-top: 1rem; }
    .text-center { text-align: center; }
    .text-muted { color: var(--gray-400); }

    /* Reset button */
    .reset-btn {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: var(--gray-100);
        border: 1px solid var(--gray-200);
        color: var(--gray-600);
        padding: 8px 16px;
        border-radius: var(--radius-sm);
        font-size: 0.85rem;
        font-weight: 500;
        cursor: pointer;
        transition: all var(--duration-fast) var(--ease-out);
    }
    .reset-btn:hover {
        background: var(--gray-200);
        color: var(--gray-700);
    }

    /* ============================================
       Animations
       ============================================ */
    @keyframes loaderPulse {
        0%, 100% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.15); opacity: 0.7; }
    }
    @keyframes dotPulse {
        0%, 100% { opacity: 0.4; transform: scale(1); }
        50% { opacity: 1; transform: scale(1.3); }
    }
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    .animate-in {
        animation: fadeInUp 0.5s var(--ease-out) both;
    }
    .animate-in-delay-1 { animation-delay: 0.1s; }
    .animate-in-delay-2 { animation-delay: 0.2s; }
    .animate-in-delay-3 { animation-delay: 0.3s; }
    .animate-in-delay-4 { animation-delay: 0.4s; }
    .animate-in-delay-5 { animation-delay: 0.5s; }

    /* Reduce motion for accessibility */
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }
    }

    /* ============================================
       Streamlit-specific overrides
       ============================================ */
    /* Remove default padding around elements */
    .stMarkdown > div > div {
        padding: 0 !important;
    }

    /* Hide streamlit's default elements we don't need */
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"] {
        display: none !important;
    }

    /* Style the default Streamlit spinner when it appears */
    [data-testid="stSpinner"] > div {
        border-top-color: var(--primary-500) !important;
    }

    /* Stale page indicator fix */
    .stSpinner > div > div {
        border-top-color: var(--primary-500) !important;
    }
    """

    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
