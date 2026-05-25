export interface GraphqlRepository {
  name: string;
  url: string;
  primaryLanguage: string | null;
  technologies: string[];
}

export interface GraphqlUserSummary {
  username: string;
  followersCount: number;
  repositories: GraphqlRepository[];
  mostUsedLanguage: string | null;
  technologies: string[];
  messages: string[];
  cached: boolean;
  authUsed: boolean;
  rateLimitLimit: number | null;
  rateLimitRemaining: number | null;
  rateLimitUsed: number | null;
  rateLimitReset: number | null;
  rateLimitResource: string | null;
}

export interface GraphqlResponse<T> {
  data?: T;
  errors?: Array<{ message: string }>;
}

export interface RestRepository {
  name: string;
  url: string;
  primary_language: string | null;
  technologies: string[];
}

export interface RestRateLimitMetadata {
  limit: number | null;
  remaining: number | null;
  used: number | null;
  reset: number | null;
  resource: string | null;
}

export interface RestUserSummary {
  username: string;
  followers_count: number;
  repositories: RestRepository[];
  most_used_language: string | null;
  technologies: string[];
  messages: string[];
  metadata?: {
    cached: boolean;
    auth_used: boolean;
    rate_limit?: RestRateLimitMetadata;
  };
}

export interface AnalysisRepositoryViewModel {
  name: string;
  url: string;
  primaryLanguage: string | null;
  technologies: string[];
}

export interface RateLimitViewModel {
  limit: number | null;
  remaining: number | null;
  used: number | null;
  reset: number | null;
  resource: string | null;
}

export interface AnalysisResultViewModel {
  username: string;
  followersCount: number;
  repositories: AnalysisRepositoryViewModel[];
  mostUsedLanguage: string | null;
  technologies: string[];
  messages: string[];
  cached: boolean;
  authUsed: boolean;
  rateLimit: RateLimitViewModel;
}
