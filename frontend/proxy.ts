import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const protectedPaths = ["/assessment", "/results", "/dashboard"];

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const sessionId = request.cookies.get("sessionid")?.value;

  const isProtected = protectedPaths.some(
    (p) => pathname === p || pathname.startsWith(p + "/")
  );

  if (isProtected && !sessionId) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("from", pathname);
    return NextResponse.redirect(loginUrl);
  }

  if ((pathname === "/login" || pathname === "/register") && sessionId) {
    return NextResponse.redirect(new URL("/assessment", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next|api|favicon.ico|file.svg|globe.svg|next.svg|vercel.svg|window.svg).*)"],
};
