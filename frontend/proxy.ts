import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const protectedPaths = ["/dashboard", "/documents", "/upload", "/profile"];
const authPaths = ["/login", "/register"];

export function proxy(request: NextRequest) {
  const token = request.cookies.get("access_token")?.value;
  const { pathname } = request.nextUrl;

  if (protectedPaths.some((path) => pathname.startsWith(path)) && !token) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  if (authPaths.some((path) => pathname.startsWith(path)) && token) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/dashboard/:path*", "/documents/:path*", "/upload/:path*", "/profile/:path*", "/login", "/register"],
};


