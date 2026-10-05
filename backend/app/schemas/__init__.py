from .ai import (
    AIAnalysisRequest,
    AIAnalysisResponse,
    AIRecommendationRequest,
    AIRecommendationResponse,
    AIStatusResponse,
)

from .auth import (
    LoginRequest,
    LoginResponse,
    UserResponse,
    CurrentUserResponse,
)

from .patient import (
    PatientBase,
    PatientCreate,
    PatientUpdate,
    PatientResponse,
    PatientListResponse,
)

from .report import (
    LabReportCreate,
    LabReportResponse,
    PathologyReportCreate,
    PathologyReportResponse,
    ImagingReportCreate,
    ImagingReportResponse,
    ImagingFileCreate,
    ImagingFileResponse,
    MolecularRecordCreate,
    MolecularRecordResponse,
)

from .workflow import (
    WORKFLOW_STATUSES,
    WorkflowUpdateRequest,
    WorkflowResponse,
    WorkflowProgressResponse,
    WorkflowHistoryResponse,
)