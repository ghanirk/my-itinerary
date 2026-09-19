export interface TripInstallment {
  id: string;
  trip_id: string;
  member_id: string;
  month_index: number;
  amount_due: number;
  amount_paid: number;
  paid_at: string | null;
  created_at: string;
}

export interface TripInstallmentPayRequest {
  // Jumlah yang dibayarkan kali ini — backend MENAMBAHKAN nilai ini ke
  // amount_paid yang sudah ada, bukan menggantinya.
  amount_paid: number;
}

export interface TripInstallmentAdjustRequest {
  new_months: number;
}
