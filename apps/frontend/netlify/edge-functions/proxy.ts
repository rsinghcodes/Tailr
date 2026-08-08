// Netlify Edge Function: proxies /api/* requests to the real backend.
// The backend origin is read from the BACKEND_ORIGIN environment variable
// (set in the Netlify dashboard), so it never appears in this repo or in
// any client-side bundle.

declare const Deno: {
  env: {
    get(key: string): string | undefined;
  };
};

export default async (request: Request): Promise<Response> => {
  const backendOrigin = Deno.env.get("BACKEND_ORIGIN");

  if (!backendOrigin) {
    return new Response("Backend origin not configured (BACKEND_ORIGIN)", { status: 502 });
  }

  const url = new URL(request.url);
  const base = backendOrigin.endsWith("/") ? backendOrigin : `${backendOrigin}/`;
  const target = new URL(url.pathname + url.search, base);

  const headers = new Headers(request.headers);
  headers.delete("host");

  const response = await fetch(target.toString(), {
    method: request.method,
    headers,
    body: request.body,
    redirect: "manual",
  });

  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers: response.headers,
  });
};
