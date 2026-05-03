/**
 * Detects restricted in-app browser environments (LinkedIn, Facebook, Instagram,
 * Twitter/X, Line, WeChat, Android WebView, iOS WebView) where Google Sign-In
 * refuses to render.
 *
 * Returns the detected app name, or null if running in a normal browser.
 */
export function getInAppBrowserName(): string | null {
  if (typeof navigator === "undefined") return null;
  const ua = navigator.userAgent;
  if (/LinkedIn/i.test(ua)) return "LinkedIn";
  if (/FBAN|FBAV/i.test(ua)) return "Facebook";
  if (/Instagram/i.test(ua)) return "Instagram";
  if (/Twitter/i.test(ua)) return "Twitter";
  if (/MicroMessenger/i.test(ua)) return "WeChat";
  if (/line\//i.test(ua)) return "Line";
  if (/Android/.test(ua) && /wv/.test(ua)) return "this app";
  if (/iPhone|iPad/.test(ua) && !/Safari/.test(ua)) return "this app";
  return null;
}

/** Returns true when running inside any restricted in-app browser. */
export function isInAppBrowser(): boolean {
  return getInAppBrowserName() !== null;
}
