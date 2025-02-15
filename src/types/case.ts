export interface Case {
  id: string;
  title: string;
  description: string;
  status: 'pending' | 'in_progress' | 'resolved' | 'archived';
  created_at: string;
  updated_at: string;
  assigned_to?: string;
  metadata?: Record<string, any>;
}

export interface CaseAnalysis {
  evaluacionPreliminar: string;
  puntosClaves: string[];
  pasosProcesales: string[];
  complejidades: string[];
}

export interface CaseDecision {
  decision: string;
  fundamentos: string[];
  fecha: string;
  juez: string;
}

export interface CaseResolution {
  resolucion: string;
  fecha: string;
  notificaciones: string[];
  siguientesPasos: string[];
}
