/**
 * Detects restricted in-app browser environments (LinkedIn, Facebook, Instagram,
 * Twitter/X, Line, WeChat, Android WebView, iOS WebView) where Google Sign-In
 * refuses to render.
 */
export function isInAppBrowser(): boolean {
  if (typeof navigator === "undefined") return false;
  const ua = navigator.userAgent;
  return (
    /LinkedIn|FBAN|FBAV|Instagram|Twitter|line\/|MicroMessenger/i.test(ua) ||
    (/Android/.test(ua) && /wv/.test(ua)) ||
    (/iPhone|iPad/.test(ua) && !/Safari/.test(ua))
  );
}
