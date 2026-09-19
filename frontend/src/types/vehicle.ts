export interface TripVehicleGroupCreateRequest {
  vehicle_label: string;
  member_ids: string[];
}

export interface TripVehicleGroupCostRequest {
  total_cost: number;
}

export interface TripVehicleGroup {
  id: string;
  trip_id: string;
  vehicle_label: string;
  total_cost: number | null;
  member_ids: string[];
}
