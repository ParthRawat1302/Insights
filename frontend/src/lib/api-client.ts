import type {
  AuthResponse,
  DashboardResponse,
  DatasetResponse,
  InsightResponse,
  LoginRequest,
  RegisterRequest,
  UserProfileResponse,
} from "./api-types";

const BACKEND_BASE_URL = import.meta.env?.VITE_BACKEND_BASE_URL ||
  "http://localhost:8000";

// Token management
export const getToken = (): string | null => {
  return localStorage.getItem("token");
};

export const setToken = (token: string): void => {
  localStorage.setItem("token", token);
};

export const clearToken = (): void => {
  localStorage.removeItem("token");
};

// Generic API call helper
export async function apiCall<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const response = await fetch(`${BACKEND_BASE_URL}${path}`, {
    credentials: "include",
    ...options,
    headers: {
      "Accept": "application/json",
      ...(options.headers || {}),
    },
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw err;
  }

  return response.json();
}

export const authAPI = {
  async register(data: RegisterRequest): Promise<AuthResponse> {
    console.log("Registering user with data:", data);
    return apiCall<AuthResponse>("/auth/register", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json",
      },
      body: JSON.stringify(data),
    });
  },


  async login(data: LoginRequest): Promise<AuthResponse> {
    const response = await fetch(`${BACKEND_BASE_URL}/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email: data.username, // or data.email
        password: data.password,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || "Login failed");
    }

    return response.json();
  },

async me(token: string): Promise<UserProfileResponse> {
  return apiCall<UserProfileResponse>("/auth/me", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}
};

// User APIs
export const userAPI = {
  async getProfile(token: string): Promise<UserProfileResponse> {
    return apiCall<UserProfileResponse>("/users/profile", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  },
};

// Dataset APIs
export const datasetAPI = {
  async upload(file: File): Promise<DatasetResponse> {
    const token = getToken();
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${BACKEND_BASE_URL}/datasets/upload`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
      },
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || "Upload failed");
    }

    return response.json();
  },

  async getAll(token:string): Promise<DatasetResponse[]> {
    return apiCall<DatasetResponse[]>("/datasets", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  },

  async getById(datasetId: string, token: string): Promise<DatasetResponse> {
    return apiCall<DatasetResponse>(`/datasets/${datasetId}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  },
};

// Dashboard APIs
export const dashboardAPI = {
  async create(datasetId: string, token: string): Promise<DashboardResponse> {
    return apiCall<DashboardResponse>(`/dashboards?dataset_id=${datasetId}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
      method: "POST",
    });
  },

  async getByDataset(datasetId: string, token: string): Promise<DashboardResponse> {
    return apiCall<DashboardResponse>(`/dashboards/by-dataset/${datasetId}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  },
};

// Insights APIs
export const insightAPI = {
  async generate(datasetId: string, token: string): Promise<void> {
    await apiCall<void>(`/insights/generate?dataset_id=${datasetId}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
      method: "POST",
    });
  },

  async get(datasetId: string, token: string): Promise<InsightResponse> {
    return apiCall<InsightResponse>(`/insights/${datasetId}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  },
};
