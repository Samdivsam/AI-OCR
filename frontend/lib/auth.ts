const TOKEN_COOKIE = "access_token";

export function setAuthToken(token: string) {
  const maxAge = 60 * 60 * 24;
  document.cookie = `${TOKEN_COOKIE}=${token}; path=/; max-age=${maxAge}; samesite=lax`;
}

export function clearAuthToken() {
  document.cookie = `${TOKEN_COOKIE}=; path=/; max-age=0; samesite=lax`;
}

export function getAuthToken(): string | null {
  const cookie = document.cookie
    .split("; ")
    .find((item) => item.startsWith(`${TOKEN_COOKIE}=`));
  return cookie ? decodeURIComponent(cookie.split("=")[1]) : null;
}

