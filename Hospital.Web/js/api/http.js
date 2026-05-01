window.hospitalHttp = {
  async request(url, options = {}) {
    const response = await fetch(url, {
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {}),
      },
      ...options,
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      if (response.status === 401) {
        window.location.href = "/login/";
        return {};
      }
      throw new Error(data.error || "Request failed.");
    }
    return data;
  },
};
