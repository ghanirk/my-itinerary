export type MemberRole = "member" | "admin";

export interface TripMemberCreateRequest {
  user_id?: string | null;
  name: string;
  origin_city: string;
  role?: MemberRole;
}

export interface TripMember {
  id: string;
  trip_id: string;
  user_id: string | null;
  name: string;
  origin_city: string;
  role: MemberRole;
  created_at: string;
}

export interface TripTransportUpdateRequest {
  price: number;
}

export interface TripTransport {
  id: string;
  trip_id: string;
  member_id: string;
  price: number;
  created_at: string;
}
