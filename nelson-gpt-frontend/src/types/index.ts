// Core application types
export interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
  preferences: UserPreferences;
  createdAt: Date;
  lastActive: Date;
}

export interface UserPreferences {
  theme: 'light' | 'dark' | 'auto';
  fontSize: 'sm' | 'base' | 'lg';
  responseStyle: 'concise' | 'detailed' | 'evidence-heavy';
  showMedicalDisclaimer: boolean;
  enableNotifications: boolean;
  autoSave: boolean;
}

// Chat-related types
export interface ChatMessage {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  citations?: Citation[];
  evidenceLevel?: EvidenceLevel;
  medicalUnits?: MedicalUnit[];
  isTyping?: boolean;
  error?: string;
}

export interface ChatSession {
  id: string;
  title: string;
  messages: ChatMessage[];
  createdAt: Date;
  updatedAt: Date;
  isPinned: boolean;
  tags: string[];
  medicalContext?: MedicalContext;
}

export interface Citation {
  id: string;
  source: string;
  chapter?: string;
  page?: string;
  url?: string;
  title: string;
  excerpt: string;
  relevanceScore: number;
}

export type EvidenceLevel = 'high' | 'moderate' | 'low' | 'expert-opinion';

export interface MedicalUnit {
  value: number;
  unit: string;
  context: string;
  normalRange?: {
    min: number;
    max: number;
    unit: string;
  };
}

export interface MedicalContext {
  patientAge?: {
    value: number;
    unit: 'days' | 'weeks' | 'months' | 'years';
  };
  weight?: {
    value: number;
    unit: 'kg' | 'lbs';
  };
  specialty?: string;
  urgency?: 'routine' | 'urgent' | 'emergency';
}

// Medical calculator types
export interface DosingCalculation {
  medication: string;
  dose: number;
  unit: string;
  frequency: string;
  route: string;
  weight: number;
  weightUnit: 'kg' | 'lbs';
  warnings: string[];
  maxDose?: number;
  minDose?: number;
}

export interface GrowthData {
  age: number;
  ageUnit: 'months' | 'years';
  weight?: number;
  height?: number;
  headCircumference?: number;
  percentiles: {
    weight?: number;
    height?: number;
    headCircumference?: number;
  };
  zScores: {
    weight?: number;
    height?: number;
    headCircumference?: number;
  };
}

export interface VaccinationRecord {
  vaccine: string;
  ageRecommended: string;
  status: 'due' | 'overdue' | 'completed' | 'contraindicated';
  dateGiven?: Date;
  notes?: string;
}

// Emergency protocol types
export interface EmergencyProtocol {
  id: string;
  title: string;
  category: 'cardiac' | 'respiratory' | 'neurological' | 'trauma' | 'poisoning' | 'other';
  severity: 'critical' | 'urgent' | 'semi-urgent';
  steps: ProtocolStep[];
  medications?: EmergencyMedication[];
  equipment?: string[];
  contraindications?: string[];
  lastUpdated: Date;
}

export interface ProtocolStep {
  order: number;
  instruction: string;
  timeframe?: string;
  critical: boolean;
  alternatives?: string[];
}

export interface EmergencyMedication {
  name: string;
  dose: string;
  route: string;
  frequency: string;
  indications: string[];
  contraindications: string[];
  sideEffects: string[];
}

// UI component types
export interface NavigationItem {
  id: string;
  label: string;
  icon: string;
  path: string;
  badge?: number;
  children?: NavigationItem[];
}

export interface ToastMessage {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  duration?: number;
  action?: {
    label: string;
    onClick: () => void;
  };
}

// API types
export interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
  errors?: string[];
  meta?: {
    total?: number;
    page?: number;
    limit?: number;
  };
}

export interface ChatRequest {
  message: string;
  sessionId?: string;
  context?: MedicalContext;
  includeEvidence?: boolean;
  responseStyle?: UserPreferences['responseStyle'];
}

export interface ChatResponse {
  message: string;
  citations: Citation[];
  evidenceLevel: EvidenceLevel;
  medicalUnits: MedicalUnit[];
  sessionId: string;
  suggestions?: string[];
}

// PWA types
export interface PWAUpdateInfo {
  available: boolean;
  version: string;
  releaseNotes?: string;
}

export interface OfflineQueueItem {
  id: string;
  type: 'chat' | 'calculation' | 'sync';
  data: any;
  timestamp: Date;
  retryCount: number;
  maxRetries: number;
}

// Accessibility types
export interface AccessibilitySettings {
  highContrast: boolean;
  reducedMotion: boolean;
  screenReaderOptimized: boolean;
  keyboardNavigation: boolean;
  fontSize: 'sm' | 'base' | 'lg' | 'xl';
}

// Medical compliance types
export interface MedicalDisclaimer {
  id: string;
  title: string;
  content: string;
  version: string;
  lastUpdated: Date;
  required: boolean;
  acknowledged?: Date;
}

export interface AuditLog {
  id: string;
  userId: string;
  action: string;
  resource: string;
  timestamp: Date;
  ipAddress?: string;
  userAgent?: string;
  details?: Record<string, any>;
}

// Error types
export interface AppError {
  code: string;
  message: string;
  details?: string;
  timestamp: Date;
  userId?: string;
  sessionId?: string;
  stack?: string;
}

// Theme types
export type ThemeMode = 'light' | 'dark' | 'auto';

export interface ThemeConfig {
  mode: ThemeMode;
  primaryColor: string;
  accentColor: string;
  borderRadius: 'none' | 'sm' | 'md' | 'lg' | 'xl';
  fontFamily: 'inter' | 'system' | 'mono';
}

// Animation types
export interface AnimationConfig {
  duration: number;
  easing: string;
  reducedMotion: boolean;
}

// Search types
export interface SearchResult {
  id: string;
  title: string;
  content: string;
  type: 'chat' | 'protocol' | 'medication' | 'condition';
  relevance: number;
  highlights: string[];
  metadata?: Record<string, any>;
}

export interface SearchFilters {
  type?: string[];
  dateRange?: {
    start: Date;
    end: Date;
  };
  evidenceLevel?: EvidenceLevel[];
  tags?: string[];
}

