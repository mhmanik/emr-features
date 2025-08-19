# EMR System Development Process
## NestJS Backend + Next.js Frontend

*Development roadmap for building a comprehensive Electronic Medical Records system*

---

## 🏗️ Architecture Overview

### Tech Stack
- **Backend**: NestJS (Node.js framework) with TypeScript
- **Frontend**: Next.js 14+ (React framework) with TypeScript
- **Database**: PostgreSQL with Prisma ORM (multi-tenant schema)
- **Authentication**: JWT + OAuth2 + RBAC
- **File Storage**: AWS S3 / Google Cloud Storage (HIPAA-compliant)
- **Real-time**: Socket.io for live updates
- **AI Integration**: OpenAI API (GPT-4, Whisper) / Azure Cognitive Services
- **Search**: Elasticsearch for medical records search
- **Cache**: Redis for session management and caching
- **Message Queue**: Bull Queue with Redis for background jobs
- **Monitoring**: Prometheus + Grafana + Sentry
- **Deployment**: Docker + Kubernetes / AWS ECS with auto-scaling

### System Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Next.js App   │────│   NestJS API    │────│   PostgreSQL    │
│   (Frontend)    │    │   (Backend)     │    │ (Multi-tenant)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         │              │   Redis Cache   │              │
         │              │  + Bull Queue   │              │
         │              └─────────────────┘              │
         │                       │                       │
         │              ┌─────────────────┐              │
         └──────────────│  Elasticsearch  │──────────────┘
                        │ (Medical Search)│
                        └─────────────────┘
                                 │
                        ┌─────────────────┐
                        │  External APIs  │
                        │ OpenAI, Twilio, │
                        │ HL7/FHIR, etc.  │
                        └─────────────────┘
```

---

## 📋 Development Phases

### Phase 1: Foundation Setup (Weeks 1-2)

#### 1.1 Project Initialization
```bash
# Backend Setup
npx @nestjs/cli new emr-backend
cd emr-backend
npm install @nestjs/config @nestjs/jwt @nestjs/passport
npm install @prisma/client prisma
npm install bcryptjs class-validator class-transformer

# Frontend Setup
npx create-next-app@latest emr-frontend --typescript --tailwind --eslint
cd emr-frontend
npm install @tanstack/react-query axios
npm install @headlessui/react @heroicons/react
```

#### 1.2 Database Schema Design
```prisma
// prisma/schema.prisma
model Tenant {
  id          String   @id @default(cuid())
  name        String
  domain      String   @unique
  settings    Json?
  users       User[]
  patients    Patient[]
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt
}

model User {
  id          String      @id @default(cuid())
  tenantId    String
  email       String
  password    String
  role        UserRole
  permissions Json?
  profile     UserProfile?
  tenant      Tenant      @relation(fields: [tenantId], references: [id])
  appointments Appointment[] @relation("DoctorAppointments")
  auditLogs   AuditLog[]
  createdAt   DateTime    @default(now())
  updatedAt   DateTime    @updatedAt
  
  @@unique([tenantId, email])
}

model Patient {
  id              String          @id @default(cuid())
  tenantId        String
  mrn             String          // Medical Record Number
  firstName       String
  lastName        String
  dateOfBirth     DateTime
  gender          String
  phone           String
  email           String?
  address         Json?
  insurance       Json?
  allergies       Allergy[]
  medicalHistory  Json?
  emergencyContact Json?
  tenant          Tenant          @relation(fields: [tenantId], references: [id])
  appointments    Appointment[]
  medicalRecords  MedicalRecord[]
  prescriptions   Prescription[]
  labResults      LabResult[]
  vitals          VitalSigns[]
  createdAt       DateTime        @default(now())
  updatedAt       DateTime        @updatedAt
  
  @@unique([tenantId, mrn])
}

model Appointment {
  id          String            @id @default(cuid())
  tenantId    String
  patientId   String
  doctorId    String
  startTime   DateTime
  endTime     DateTime
  status      AppointmentStatus
  type        String
  notes       String?
  location    String?
  patient     Patient           @relation(fields: [patientId], references: [id])
  doctor      User              @relation("DoctorAppointments", fields: [doctorId], references: [id])
  createdAt   DateTime          @default(now())
  updatedAt   DateTime          @updatedAt
}

model MedicalRecord {
  id          String   @id @default(cuid())
  patientId   String
  doctorId    String
  visitDate   DateTime
  chiefComplaint String
  soap        Json     // Subjective, Objective, Assessment, Plan
  diagnosis   String[]
  icdCodes    String[]
  aiGenerated Boolean  @default(false)
  patient     Patient  @relation(fields: [patientId], references: [id])
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt
}

model Prescription {
  id            String   @id @default(cuid())
  patientId     String
  doctorId      String
  medication    String
  dosage        String
  frequency     String
  duration      String
  instructions  String?
  status        PrescriptionStatus
  digitalSignature String?
  patient       Patient  @relation(fields: [patientId], references: [id])
  createdAt     DateTime @default(now())
  updatedAt     DateTime @updatedAt
}

model AuditLog {
  id        String   @id @default(cuid())
  userId    String
  action    String
  resource  String
  details   Json?
  ipAddress String?
  userAgent String?
  user      User     @relation(fields: [userId], references: [id])
  createdAt DateTime @default(now())
}

enum UserRole {
  ADMIN
  DOCTOR
  NURSE
  LAB_TECH
  PHARMACIST
  PATIENT
}

enum AppointmentStatus {
  SCHEDULED
  CONFIRMED
  IN_PROGRESS
  COMPLETED
  CANCELLED
  NO_SHOW
}

enum PrescriptionStatus {
  PENDING
  SENT_TO_PHARMACY
  FILLED
  CANCELLED
}
```

#### 1.3 Authentication System
```typescript
// Backend: auth.service.ts
@Injectable()
export class AuthService {
  async validateUser(email: string, password: string) {
    // JWT validation logic
  }
  
  async login(user: any) {
    // Login implementation
  }
}

// Frontend: auth context
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  // Auth context implementation
};
```

### Phase 2: Core Modules Development (Weeks 3-8)

#### 2.1 Patient Management Module (Week 3)

**Backend Implementation:**
```typescript
// patients.controller.ts
@Controller('patients')
export class PatientsController {
  @Post()
  async createPatient(@Body() createPatientDto: CreatePatientDto) {
    return this.patientsService.create(createPatientDto);
  }

  @Get()
  async findAll(@Query() query: PaginationDto) {
    return this.patientsService.findAll(query);
  }

  @Get(':id')
  async findOne(@Param('id') id: string) {
    return this.patientsService.findOne(id);
  }
}
```

**Frontend Implementation:**
```typescript
// pages/patients/index.tsx
export default function PatientsPage() {
  const { data: patients, isLoading } = useQuery({
    queryKey: ['patients'],
    queryFn: () => api.get('/patients').then(res => res.data)
  });

  return (
    <div className="container mx-auto px-4">
      <PatientList patients={patients} />
      <PatientForm />
    </div>
  );
}
```

#### 2.2 Appointment Scheduling (Week 4)

**Features to Implement:**
- Calendar integration
- Multi-doctor scheduling
- Automated reminders
- Conflict detection

```typescript
// appointments.service.ts
@Injectable()
export class AppointmentsService {
  async scheduleAppointment(appointmentData: CreateAppointmentDto) {
    // Check availability
    // Create appointment
    // Send notifications
  }

  async getAvailableSlots(doctorId: string, date: Date) {
    // Calculate available time slots
  }
}
```

#### 2.3 AI Clinical Documentation (Week 5)

**Voice-to-Text Integration:**
```typescript
// ai.service.ts
@Injectable()
export class AIService {
  constructor(
    private readonly openai: OpenAI,
    private readonly configService: ConfigService,
  ) {}

  async transcribeAudio(audioBuffer: Buffer, language = 'en'): Promise<string> {
    try {
      const response = await this.openai.audio.transcriptions.create({
        file: audioBuffer,
        model: "whisper-1",
        language,
        response_format: "json",
        temperature: 0.2,
      });
      return response.text;
    } catch (error) {
      throw new BadRequestException('Audio transcription failed');
    }
  }

  async generateSOAPNote(transcript: string, patientContext?: any): Promise<SOAPNote> {
    const prompt = `
      Convert the following medical consultation transcript into a structured SOAP note:
      
      Transcript: ${transcript}
      ${patientContext ? `Patient Context: ${JSON.stringify(patientContext)}` : ''}
      
      Please format as:
      - Subjective: Patient's reported symptoms and concerns
      - Objective: Observable findings and measurements
      - Assessment: Clinical impression and diagnosis
      - Plan: Treatment plan and follow-up
    `;

    const response = await this.openai.chat.completions.create({
      model: "gpt-4",
      messages: [{ role: "user", content: prompt }],
      temperature: 0.3,
      max_tokens: 1000,
    });

    return this.parseSOAPNote(response.choices[0].message.content);
  }

  async generateMedicalCodes(diagnosis: string): Promise<{ icd10: string[], cpt: string[] }> {
    const prompt = `
      Generate appropriate ICD-10 and CPT codes for the following diagnosis/procedure:
      ${diagnosis}
      
      Return in JSON format: {"icd10": ["code1", "code2"], "cpt": ["code1", "code2"]}
    `;

    const response = await this.openai.chat.completions.create({
      model: "gpt-4",
      messages: [{ role: "user", content: prompt }],
      temperature: 0.1,
    });

    return JSON.parse(response.choices[0].message.content);
  }

  private parseSOAPNote(content: string): SOAPNote {
    // Parse the AI response into structured SOAP format
    const sections = content.split(/(?=Subjective:|Objective:|Assessment:|Plan:)/i);
    return {
      subjective: this.extractSection(sections, 'Subjective'),
      objective: this.extractSection(sections, 'Objective'),
      assessment: this.extractSection(sections, 'Assessment'),
      plan: this.extractSection(sections, 'Plan'),
    };
  }
}
```

#### 2.4 E-Prescription Module (Week 6)

**Drug Database Integration:**
```typescript
// prescriptions.service.ts
@Injectable()
export class PrescriptionsService {
  async checkDrugInteractions(medications: string[]) {
    // Drug interaction checking logic
  }

  async createPrescription(prescriptionData: CreatePrescriptionDto) {
    // Digital signature validation
    // Create prescription
    // Notify pharmacy
  }
}
```

#### 2.5 Lab & Imaging Module (Week 7)

**File Upload & Processing:**
```typescript
// lab-results.controller.ts
@Controller('lab-results')
export class LabResultsController {
  @Post('upload')
  @UseInterceptors(FileInterceptor('file'))
  async uploadResult(@UploadedFile() file: Express.Multer.File) {
    // Process and store lab results
    // Optional AI analysis
  }
}
```

#### 2.6 Patient Portal (Week 8)

**Patient-facing Features:**
```typescript
// Frontend: patient portal
export default function PatientPortal() {
  return (
    <div className="patient-dashboard">
      <HealthRecords />
      <AppointmentBooking />
      <SecureMessaging />
      <AIHealthBot />
    </div>
  );
}
```

### Phase 3: Advanced Features (Weeks 9-12)

#### 3.1 Clinical Decision Support System (Week 9)

**Real-time Alerts & AI Decision Support:**
```typescript
// cdss.service.ts
@Injectable()
export class CDSSService {
  constructor(
    private readonly aiService: AIService,
    private readonly alertService: AlertService,
  ) {}

  async analyzeVitals(patientId: string, vitals: VitalSigns): Promise<Alert[]> {
    const alerts = [];
    const patient = await this.getPatientWithHistory(patientId);
    
    // Critical vital signs checks
    if (vitals.bloodPressure.systolic > 180 || vitals.bloodPressure.diastolic > 120) {
      alerts.push({
        type: 'HYPERTENSIVE_CRISIS',
        severity: 'CRITICAL',
        message: 'Hypertensive crisis - immediate intervention required',
        recommendations: ['Check BP in 5 minutes', 'Consider IV antihypertensives']
      });
    }

    if (vitals.heartRate > 100 && vitals.temperature > 38.5) {
      alerts.push({
        type: 'SEPSIS_RISK',
        severity: 'HIGH',
        message: 'Possible sepsis - SIRS criteria met',
        recommendations: ['Order blood cultures', 'Consider broad-spectrum antibiotics']
      });
    }

    // AI-powered risk assessment
    const riskAssessment = await this.assessChronicDiseaseRisk(patient, vitals);
    if (riskAssessment.diabetesRisk > 0.7) {
      alerts.push({
        type: 'DIABETES_RISK',
        severity: 'MEDIUM',
        message: `High diabetes risk detected (${(riskAssessment.diabetesRisk * 100).toFixed(1)}%)`,
        recommendations: ['Order HbA1c', 'Lifestyle counseling']
      });
    }

    // Drug interaction checks
    const drugAlerts = await this.checkDrugInteractions(patient.currentMedications, vitals);
    alerts.push(...drugAlerts);

    return alerts;
  }

  async generateDiagnosticSuggestions(symptoms: string[], vitals: VitalSigns, history: any): Promise<DiagnosticSuggestion[]> {
    const prompt = `
      Based on the following clinical data, suggest possible diagnoses with confidence scores:
      
      Symptoms: ${symptoms.join(', ')}
      Vital Signs: ${JSON.stringify(vitals)}
      Medical History: ${JSON.stringify(history)}
      
      Provide top 5 differential diagnoses with reasoning and recommended tests.
    `;

    const response = await this.aiService.generateClinicalInsight(prompt);
    return this.parseDiagnosticSuggestions(response);
  }

  private async assessChronicDiseaseRisk(patient: any, vitals: VitalSigns): Promise<RiskAssessment> {
    // AI-powered chronic disease risk stratification
    const features = {
      age: this.calculateAge(patient.dateOfBirth),
      bmi: vitals.weight / Math.pow(vitals.height / 100, 2),
      bloodPressure: vitals.bloodPressure,
      familyHistory: patient.familyHistory,
      lifestyle: patient.lifestyleFactors
    };

    return await this.aiService.assessDiseaseRisk(features);
  }
}
```

#### 3.2 Billing & Claims (Week 10)

**Insurance Integration:**
```typescript
// billing.service.ts
@Injectable()
export class BillingService {
  async generateClaim(encounter: Encounter): Promise<Claim> {
    // Auto-generate CPT/ICD-10 codes
    // Create insurance claim
    // Submit electronically
  }

  async checkEligibility(patientId: string, insuranceId: string) {
    // Real-time eligibility verification
  }
}
```

#### 3.3 Analytics Dashboard (Week 11)

**Admin Analytics:**
```typescript
// analytics.service.ts
@Injectable()
export class AnalyticsService {
  async getPatientMetrics(hospitalId: string) {
    return {
      totalPatients: await this.getTotalPatients(hospitalId),
      appointmentsToday: await this.getTodayAppointments(hospitalId),
      revenue: await this.getRevenue(hospitalId),
      aiUsageStats: await this.getAIUsage(hospitalId)
    };
  }
}
```

#### 3.4 System Management (Week 12)

**Multi-tenant Architecture:**
```typescript
// tenant.guard.ts
@Injectable()
export class TenantGuard implements CanActivate {
  canActivate(context: ExecutionContext): boolean {
    const request = context.switchToHttp().getRequest();
    const tenantId = request.headers['x-tenant-id'];
    
    // Validate tenant access
    return this.validateTenant(tenantId);
  }
}
```

### Phase 4: Security & Compliance (Weeks 13-14)

#### 4.1 HIPAA Compliance Implementation

**Comprehensive Audit Logging:**
```typescript
// audit.service.ts
@Injectable()
export class AuditService {
  constructor(
    private readonly auditRepository: AuditRepository,
    private readonly encryptionService: EncryptionService,
  ) {}

  async logAccess(userId: string, resource: string, action: string, details?: any, request?: any) {
    const auditEntry = {
      userId,
      resource,
      action,
      details: details ? this.encryptionService.encrypt(JSON.stringify(details)) : null,
      ipAddress: this.getClientIP(request),
      userAgent: request?.headers['user-agent'],
      sessionId: request?.sessionID,
      timestamp: new Date(),
      success: true,
    };

    await this.auditRepository.create(auditEntry);
    
    // Real-time anomaly detection
    await this.detectAnomalousActivity(userId, action, auditEntry);
  }

  async logFailedAccess(userId: string, resource: string, action: string, error: string, request?: any) {
    await this.auditRepository.create({
      userId,
      resource,
      action,
      error: this.encryptionService.encrypt(error),
      ipAddress: this.getClientIP(request),
      userAgent: request?.headers['user-agent'],
      timestamp: new Date(),
      success: false,
    });
  }

  private async detectAnomalousActivity(userId: string, action: string, currentEntry: any) {
    // Check for suspicious patterns
    const recentActivity = await this.getRecentActivity(userId, 24); // Last 24 hours
    
    // Multiple failed login attempts
    const failedLogins = recentActivity.filter(a => a.action === 'LOGIN' && !a.success);
    if (failedLogins.length > 5) {
      await this.triggerSecurityAlert('MULTIPLE_FAILED_LOGINS', userId, currentEntry);
    }

    // Unusual access patterns (e.g., accessing records outside normal hours)
    const hour = new Date().getHours();
    if ((hour < 6 || hour > 22) && action === 'VIEW_PATIENT_RECORD') {
      await this.triggerSecurityAlert('OFF_HOURS_ACCESS', userId, currentEntry);
    }

    // Bulk data access
    const dataAccessCount = recentActivity.filter(a => a.action.includes('VIEW')).length;
    if (dataAccessCount > 100) {
      await this.triggerSecurityAlert('BULK_DATA_ACCESS', userId, currentEntry);
    }
  }

  private async triggerSecurityAlert(alertType: string, userId: string, details: any) {
    // Send alert to security team
    // Log security incident
    // Potentially lock account if critical
  }
}
```

**Advanced Data Encryption & Security:**
```typescript
// encryption.service.ts
@Injectable()
export class EncryptionService {
  private readonly algorithm = 'aes-256-gcm';
  private readonly keyDerivation = 'pbkdf2';
  
  constructor(private readonly configService: ConfigService) {}

  encryptPHI(data: string, additionalData?: string): EncryptedData {
    const key = this.deriveKey();
    const iv = crypto.randomBytes(16);
    const cipher = crypto.createCipher(this.algorithm, key);
    
    if (additionalData) {
      cipher.setAAD(Buffer.from(additionalData));
    }
    
    let encrypted = cipher.update(data, 'utf8', 'hex');
    encrypted += cipher.final('hex');
    
    const authTag = cipher.getAuthTag();
    
    return {
      encryptedData: encrypted,
      iv: iv.toString('hex'),
      authTag: authTag.toString('hex'),
      algorithm: this.algorithm
    };
  }

  decryptPHI(encryptedData: EncryptedData, additionalData?: string): string {
    const key = this.deriveKey();
    const decipher = crypto.createDecipher(this.algorithm, key);
    
    decipher.setAuthTag(Buffer.from(encryptedData.authTag, 'hex'));
    
    if (additionalData) {
      decipher.setAAD(Buffer.from(additionalData));
    }
    
    let decrypted = decipher.update(encryptedData.encryptedData, 'hex', 'utf8');
    decrypted += decipher.final('utf8');
    
    return decrypted;
  }

  hashPassword(password: string): Promise<string> {
    return bcrypt.hash(password, 12);
  }

  verifyPassword(password: string, hash: string): Promise<boolean> {
    return bcrypt.compare(password, hash);
  }

  private deriveKey(): Buffer {
    const masterKey = this.configService.get<string>('ENCRYPTION_MASTER_KEY');
    const salt = this.configService.get<string>('ENCRYPTION_SALT');
    return crypto.pbkdf2Sync(masterKey, salt, 100000, 32, 'sha512');
  }

  // Field-level encryption for database
  @Transform(({ value }) => value ? this.encryptPHI(value) : value)
  encryptField(value: string): EncryptedData {
    return this.encryptPHI(value);
  }

  @Transform(({ value }) => value ? this.decryptPHI(value) : value)
  decryptField(value: EncryptedData): string {
    return this.decryptPHI(value);
  }
}
```

#### 4.2 Role-Based Access Control

```typescript
// rbac.guard.ts
@Injectable()
export class RBACGuard implements CanActivate {
  canActivate(context: ExecutionContext): boolean {
    const requiredRoles = this.reflector.get<string[]>('roles', context.getHandler());
    const user = context.switchToHttp().getRequest().user;
    
    return requiredRoles.some(role => user.roles.includes(role));
  }
}
```

### Phase 5: Testing & Deployment (Weeks 15-16)

#### 5.1 Testing Strategy

**Unit Tests:**
```typescript
// patients.service.spec.ts
describe('PatientsService', () => {
  it('should create a patient', async () => {
    const patientData = { firstName: 'John', lastName: 'Doe' };
    const result = await service.create(patientData);
    expect(result).toBeDefined();
  });
});
```

**Integration Tests:**
```typescript
// app.e2e-spec.ts
describe('AppController (e2e)', () => {
  it('/patients (POST)', () => {
    return request(app.getHttpServer())
      .post('/patients')
      .send(patientData)
      .expect(201);
  });
});
```

#### 5.2 Deployment Configuration

**Docker Setup:**
```dockerfile
# Backend Dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "run", "start:prod"]
```

**Kubernetes Deployment:**
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: emr-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: emr-backend
  template:
    metadata:
      labels:
        app: emr-backend
    spec:
      containers:
      - name: emr-backend
        image: emr-backend:latest
        ports:
        - containerPort: 3000
```

---

## 🔧 Development Best Practices

### Code Quality
- **ESLint + Prettier** for consistent formatting
- **Husky** for pre-commit hooks
- **Jest** for unit testing
- **Cypress** for E2E testing

### Security Measures
- Input validation with **class-validator**
- SQL injection prevention with **Prisma**
- Rate limiting with **@nestjs/throttler**
- CORS configuration
- Helmet.js for security headers

### Performance Optimization
- Database indexing strategy
- Redis caching for frequently accessed data
- Image optimization for medical files
- Lazy loading for large datasets
- API response compression

### Monitoring & Logging
- **Winston** for structured logging
- **Prometheus** metrics collection
- **Grafana** dashboards
- **Sentry** for error tracking
- Health check endpoints

---

## 📊 Project Timeline

| Phase | Duration | Key Deliverables |
|-------|----------|------------------|
| Phase 1 | 2 weeks | Project setup, auth, basic CRUD |
| Phase 2 | 6 weeks | Core modules (Patient, Appointments, AI, Prescriptions, Lab, Portal) |
| Phase 3 | 4 weeks | Advanced features (CDSS, Billing, Analytics, Management) |
| Phase 4 | 2 weeks | Security, compliance, RBAC |
| Phase 5 | 2 weeks | Testing, deployment, documentation |

**Total Duration: 16 weeks**

---

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- PostgreSQL 14+
- Redis 6+
- Docker & Docker Compose

### Quick Start
```bash
# Clone repositories
git clone <emr-backend-repo>
git clone <emr-frontend-repo>

# Setup backend
cd emr-backend
npm install
npx prisma migrate dev
npm run start:dev

# Setup frontend
cd emr-frontend
npm install
npm run dev
```

### Environment Variables
```env
# Backend .env
DATABASE_URL="postgresql://user:password@localhost:5432/emr"
REDIS_URL="redis://localhost:6379"
JWT_SECRET="your-jwt-secret-min-32-chars"
JWT_REFRESH_SECRET="your-refresh-secret-min-32-chars"
ENCRYPTION_MASTER_KEY="your-encryption-master-key-64-chars"
ENCRYPTION_SALT="your-encryption-salt-32-chars"

# AI Services
OPENAI_API_KEY="your-openai-key"
OPENAI_ORG_ID="your-openai-org-id"

# Cloud Storage
AWS_ACCESS_KEY_ID="your-aws-key"
AWS_SECRET_ACCESS_KEY="your-aws-secret"
AWS_REGION="us-east-1"
AWS_S3_BUCKET="emr-documents-bucket"

# External APIs
TWILIO_ACCOUNT_SID="your-twilio-sid"
TWILIO_AUTH_TOKEN="your-twilio-token"
SENDGRID_API_KEY="your-sendgrid-key"

# Monitoring
SENTRY_DSN="your-sentry-dsn"
PROMETHEUS_ENDPOINT="http://localhost:9090"

# HIPAA Compliance
AUDIT_LOG_RETENTION_DAYS=2555  # 7 years
SESSION_TIMEOUT_MINUTES=30
PASSWORD_COMPLEXITY_ENABLED=true

# Frontend .env.local
NEXT_PUBLIC_API_URL="http://localhost:3001"
NEXT_PUBLIC_SOCKET_URL="http://localhost:3001"
NEXT_PUBLIC_SENTRY_DSN="your-frontend-sentry-dsn"
NEXT_PUBLIC_APP_VERSION="1.0.0"
```

---

## 📚 Additional Resources

- [NestJS Documentation](https://docs.nestjs.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Prisma Documentation](https://www.prisma.io/docs)
- [HIPAA Compliance Guide](https://www.hhs.gov/hipaa/index.html)
- [HL7 FHIR Standards](https://www.hl7.org/fhir/)

---

*This development process provides a comprehensive roadmap for building a production-ready EMR system with modern technologies and best practices.*
