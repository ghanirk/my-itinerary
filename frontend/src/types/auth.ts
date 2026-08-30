export interface UserRegisterRequest {
  name: string;
  email: string;
  password: string;
}

export interface UserLoginRequest {
  email: string;
  password: string;
}

export interface UserOut {
  id: string;
  name: string;
  email: string;
  is_premium_trial_used: boolean;
}

export interface Token {
  access_token: string;
  token_type: string;
  user: UserOut;
}
