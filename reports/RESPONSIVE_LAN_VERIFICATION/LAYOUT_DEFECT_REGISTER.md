# Mobile & Multi-Device Layout Defect Register

**Project:** SochnaSetu AI — Notice-to-Action Accessibility Assistant  
**Date:** October 24, 2026  
**Auditor:** Antigravity AI Engineering Team  
**Scope:** Responsive Layout Defect Catalog, Root Causes, and Verification Status

---

## 1. Defect Catalog & Resolution Matrix

| Defect ID | Severity | Component / Area | Root Cause Description | Resolution Implemented | Test Status |
|-----------|----------|------------------|------------------------|------------------------|-------------|
| **DEF-MOB-01** | **CRITICAL** | `Sidebar.tsx` / Layout | Sidebar had fixed width (`w-64` / 256px) without responsive hide rules (`md:flex`), occupying 75%–80% of phone viewports (320px–360px). | Replaced with `hidden md:flex flex-col w-64` for desktop and implemented a slide-over drawer triggered by header hamburger menu on `< md`. | **PASS** |
| **DEF-MOB-02** | **CRITICAL** | `ApplicationLayout.tsx` | Root container lacked `overflow-x-hidden`, allowing unconstrained child elements to trigger page-level horizontal scroll on touch devices. | Added `overflow-x-hidden w-full min-w-0` to root application wrapper; ensured viewport width lock. | **PASS** |
| **DEF-MOB-03** | **HIGH** | `index.html` | Missing mobile viewport configuration for proper device scaling and notch safe-area handling. | Added `<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, viewport-fit=cover" />` and web app meta tags. | **PASS** |
| **DEF-MOB-04** | **HIGH** | Navigation Architecture | No mobile-optimized bottom navigation; mobile users had to scroll extensively or struggle with desktop navigation links. | Created `MobileBottomNav.tsx` (`md:hidden`) with 5 thumb-friendly touch targets (Home, Ingest, Facts, Actions, Menu). | **PASS** |
| **DEF-MOB-05** | **HIGH** | `VoiceGuidanceBar.tsx` | Floating voice guidance bar fixed at `bottom-4` overlapped the new mobile bottom navigation on mobile devices. | Adjusted mobile positioning to `bottom-16 md:bottom-4` with `z-40` clearance. | **PASS** |
| **DEF-MOB-06** | **HIGH** | `ActionChecklistTable.tsx` | Wide data table forced mobile viewport expansion and clipped task names and date columns. | Wrapped table in `overflow-x-auto -mx-4 sm:mx-0 px-4 sm:px-0`; refactored action buttons and category pills to wrap cleanly. | **PASS** |
| **DEF-MOB-07** | **MEDIUM** | `DashboardView.tsx` | Hero banner used rigid `p-10` padding and `text-5xl` heading, causing awkward line breaks and overflow on 320px–360px screens. | Applied responsive font scaling (`text-2xl sm:text-4xl md:text-5xl`) and adaptive padding (`p-4 sm:p-8 md:p-10`); flexed action buttons to full-width stack on mobile. | **PASS** |
| **DEF-MOB-08** | **MEDIUM** | `Header.tsx` | Header search input and language selector competed for space, causing overflow on narrow screens. | Added mobile toggle (`md:hidden`), collapsed branding elements, and streamlined language selector for mobile displays. | **PASS** |
| **DEF-MOB-09** | **MEDIUM** | `ConfirmationModal.tsx` & `OriginalNoticeViewerModal.tsx` | Dialog modals had fixed widths (`w-[600px]`, `w-[800px]`), extending beyond the screen edge on mobile. | Changed modal containers to `w-full max-w-lg mx-3 sm:mx-auto max-h-[90vh] overflow-y-auto`. | **PASS** |
| **DEF-MOB-10** | **LOW** | Touch Targets & Inputs | Small buttons and links had hitboxes under 36px, causing missed taps on touchscreens. | Standardized all interactive elements to WCAG 2.1 AA compliant `min-h-[44px]` touch targets. | **PASS** |

---

## 2. Regression Prevention & Verification

All 10 defects were verified through the Vitest Responsive Viewport Matrix test suite:
- File: [`frontend/src/test/ResponsiveViewportMatrix.test.tsx`](file:///C:/Users/Avinash/OneDrive/Desktop/AI-Projects/Hacktober%20fest/ps2/frontend/src/test/ResponsiveViewportMatrix.test.tsx)
- Outcome: 8/8 viewports passing without horizontal overflow, component collisions, or broken layouts.
