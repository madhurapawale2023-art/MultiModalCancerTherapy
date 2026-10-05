(function () {
    "use strict";

    angular
        .module("MultiModalCancerTherapy")
        .controller("AIController", AIController);

    AIController.$inject = [
        "$scope",
        "$location",
        "$q",
        "ApiService",
        "AuthService"
    ];

    function AIController(
        $scope,
        $location,
        $q,
        ApiService,
        AuthService
    ) {

        // =========================================================
        // INITIAL STATE
        // =========================================================

        $scope.loading = false;
        $scope.analyzing = false;
        $scope.uploading = false;

        $scope.errorMessage = "";
        $scope.successMessage = "";

        $scope.currentUser = AuthService.getCurrentUser();

        $scope.patients = [];

        $scope.selectedPatientId =
            $location.search().patientId || "";

        $scope.selectedPatient = null;


        // =========================================================
        // AI STATUS
        // =========================================================

        $scope.aiStatus = {
            status: "checking",

            clinical_model: false,
            clinical_preprocessor: false,
            target_encoder: false,

            ultrasound_model: false,
            ultrasound_model_info: false,

            clinical_decision_support_only: true,
            senior_doctor_review_required: true
        };


        // =========================================================
        // CLINICAL DATA
        // =========================================================

        $scope.clinicalData = {

            age: null,
            sex: "",

            on_thyroxine: false,
            query_on_thyroxine: false,
            on_antithyroid_meds: false,
            sick: false,
            pregnant: false,
            thyroid_surgery: false,
            I131_treatment: false,
            query_hypothyroid: false,
            query_hyperthyroid: false,
            lithium: false,
            goitre: false,
            tumor: false,
            hypopituitary: false,
            psych: false,

            TSH_measured: false,
            TSH: null,
            T3_measured: false,
            T3: null,
            TT4_measured: false,
            TT4: null,
            T4U_measured: false,
            T4U: null,
            FTI_measured: false,
            FTI: null,
            TBG_measured: false,

            referral_source: ""
        };


        // =========================================================
        // RESULTS
        // =========================================================

        $scope.clinicalResult = null;

        $scope.ultrasoundResult = null;

        $scope.multimodalResult = null;

        $scope.clinicalPrediction = null;

        $scope.clinicalProbability = null;

        $scope.ultrasoundEvidence = null;

        $scope.requiresDoctorReview = true;


        // =========================================================
        // ULTRASOUND FILE
        // =========================================================

        $scope.selectedFile = null;

        $scope.filePreviewUrl = "";

        $scope.uploadResponse = null;


        // =========================================================
        // INITIALIZE
        // =========================================================

        $scope.initialize = function () {

            $scope.loading = true;

            $scope.errorMessage = "";
            $scope.successMessage = "";

            return $q.all({

                patients: loadPatients(),

                aiStatus: loadAIStatus()

            })
            .then(function (result) {

                if (result.patients) {

                    processPatients(
                        result.patients
                    );
                }

                if (result.aiStatus) {

                    processAIStatus(
                        result.aiStatus
                    );
                }

                if ($scope.selectedPatientId) {

                    selectPatientById(
                        $scope.selectedPatientId
                    );
                }

            })
            .catch(function (error) {

                console.error(
                    "AI page initialization error:",
                    error
                );

                $scope.errorMessage =
                    error && error.message
                        ? error.message
                        : "Unable to load AI analysis page.";

            })
            .finally(function () {

                $scope.loading = false;
            });
        };


        // =========================================================
        // LOAD PATIENTS
        // =========================================================

        function loadPatients() {

            return ApiService.getPatients({

                page: 1,

                page_size: 100

            })
            .then(function (data) {

                return data;

            })
            .catch(function (error) {

                console.warn(
                    "Unable to load patients:",
                    error
                );

                return {
                    items: [],
                    total: 0
                };
            });
        }


        // =========================================================
        // PROCESS PATIENTS
        // =========================================================

        function processPatients(data) {

            if (Array.isArray(data)) {

                $scope.patients = data;

            }
            else if (
                data &&
                Array.isArray(data.items)
            ) {

                $scope.patients =
                    data.items;

            }
            else {

                $scope.patients = [];
            }
        }


        // =========================================================
        // SELECT PATIENT BY ID
        // =========================================================

        function selectPatientById(patientId) {

            if (!patientId) {
                return;
            }

            var patient =
                $scope.patients.find(
                    function (item) {

                        return String(item.id) ===
                            String(patientId);

                    }
                );

            if (patient) {

                $scope.selectedPatient =
                    patient;

                populateClinicalData(
                    patient
                );
            }
        }


        // =========================================================
        // PATIENT CHANGE
        // =========================================================

        $scope.onPatientChange = function () {

            $scope.errorMessage = "";
            $scope.successMessage = "";

            $scope.selectedPatient = null;

            $scope.clinicalResult = null;

            $scope.ultrasoundResult = null;

            $scope.multimodalResult = null;

            if (!$scope.selectedPatientId) {

                $location.search(
                    "patientId",
                    null
                );

                return;
            }

            var patientId =
                $scope.selectedPatientId;

            var existing =
                $scope.patients.find(
                    function (patient) {

                        return String(patient.id) ===
                            String(patientId);

                    }
                );

            if (existing) {

                $scope.selectedPatient =
                    existing;

                populateClinicalData(
                    existing
                );

            }
            else {

                ApiService.getPatient(
                    patientId
                )
                .then(function (patient) {

                    $scope.selectedPatient =
                        patient;

                    populateClinicalData(
                        patient
                    );

                })
                .catch(function (error) {

                    $scope.errorMessage =
                        error && error.message
                            ? error.message
                            : "Unable to load selected patient.";
                });
            }

            $location.search(
                "patientId",
                patientId
            );
        };


        // =========================================================
        // POPULATE CLINICAL DATA
        // =========================================================

        function populateClinicalData(patient) {

            if (!patient) {
                return;
            }

            if (
                patient.age !== undefined &&
                patient.age !== null
            ) {

                $scope.clinicalData.age =
                    patient.age;
            }

            if (patient.sex) {

                $scope.clinicalData.sex =
                    patient.sex;
            }

            if (patient.clinical_notes) {

                $scope.clinicalData.clinical_notes =
                    patient.clinical_notes;
            }

            if (patient.referral_source) {

                $scope.clinicalData.referral_source =
                    patient.referral_source;
            }
        }


        // =========================================================
        // LOAD AI STATUS
        // =========================================================

        function loadAIStatus() {

            return ApiService.getAIStatus()
                .then(function (data) {

                    return data;

                })
                .catch(function (error) {

                    console.warn(
                        "AI status error:",
                        error
                    );

                    return null;
                });
        }


        // =========================================================
        // PROCESS AI STATUS
        // =========================================================

        function processAIStatus(data) {

            if (!data) {
                return;
            }

            $scope.aiStatus =
                angular.extend(
                    $scope.aiStatus,
                    data
                );
        }


        // =========================================================
        // AI READY
        // =========================================================

        $scope.isAIReady = function () {

            var status =
                String(
                    $scope.aiStatus.status || ""
                ).toLowerCase();

            return (
                status === "ready" ||
                status === "active"
            );
        };


        // =========================================================
        // RUN CLINICAL AI
        // =========================================================

        $scope.runClinicalAI = function () {

            $scope.errorMessage = "";
            $scope.successMessage = "";

            if (!$scope.selectedPatientId) {

                $scope.errorMessage =
                    "Please select a patient first.";

                return;
            }

            if (!$scope.isAIReady()) {

                $scope.errorMessage =
                    "AI service is not ready.";

                return;
            }

            if (!$scope.clinicalData.age) {

                $scope.errorMessage =
                    "Patient age is required.";

                return;
            }

            if (!$scope.clinicalData.sex) {

                $scope.errorMessage =
                    "Patient sex is required.";

                return;
            }

            $scope.analyzing = true;

            var payload =
                angular.copy(
                    $scope.clinicalData
                );

            payload.patient_id =
                Number(
                    $scope.selectedPatientId
                );

            ApiService.runClinicalAI(
                payload
            )
            .then(function (data) {

                $scope.clinicalResult =
                    data;

                $scope.clinicalPrediction =
                    data.clinical_top_prediction ||
                    data.prediction ||
                    data.top_prediction ||
                    null;

                $scope.clinicalProbability =
                    data.clinical_top_probability ||
                    data.probability ||
                    data.confidence ||
                    null;

                $scope.requiresDoctorReview =
                    true;

                $scope.successMessage =
                    "Clinical AI analysis completed. "
                    + "Doctor review is required.";

            })
            .catch(function (error) {

                console.error(
                    "Clinical AI error:",
                    error
                );

                $scope.errorMessage =
                    error && error.message
                        ? error.message
                        : "Clinical AI analysis failed.";

            })
            .finally(function () {

                $scope.analyzing = false;
            });
        };


        // =========================================================
        // FILE SELECTION
        // =========================================================

        $scope.onFileSelected = function (element) {

            $scope.errorMessage = "";
            $scope.successMessage = "";

            var files =
                element && element.files
                    ? element.files
                    : [];

            if (!files.length) {
                return;
            }

            var file =
                files[0];

            var allowedTypes = [

                "image/jpeg",

                "image/jpg",

                "image/png",

                "image/webp"

            ];

            if (
                file.type &&
                allowedTypes.indexOf(file.type) === -1
            ) {

                $scope.selectedFile = null;

                $scope.filePreviewUrl = "";

                $scope.errorMessage =
                    "Please select a JPG, JPEG, PNG or WEBP ultrasound image.";

                return;
            }

            var maxSize =
                10 * 1024 * 1024;

            if (file.size > maxSize) {

                $scope.selectedFile = null;

                $scope.filePreviewUrl = "";

                $scope.errorMessage =
                    "Maximum ultrasound image size is 10 MB.";

                return;
            }

            $scope.selectedFile =
                file;

            if ($scope.filePreviewUrl) {

                URL.revokeObjectURL(
                    $scope.filePreviewUrl
                );
            }

            $scope.filePreviewUrl =
                URL.createObjectURL(
                    file
                );

            $scope.$applyAsync();
        };


        // =========================================================
        // CLEAR FILE
        // =========================================================

        $scope.clearSelectedFile = function () {

            if ($scope.filePreviewUrl) {

                URL.revokeObjectURL(
                    $scope.filePreviewUrl
                );
            }

            $scope.selectedFile = null;

            $scope.filePreviewUrl = "";

            $scope.uploadResponse = null;
        };


        // =========================================================
        // UPLOAD ULTRASOUND
        // =========================================================

        $scope.uploadUltrasound = function () {

            $scope.errorMessage = "";
            $scope.successMessage = "";

            if (!$scope.selectedPatientId) {

                $scope.errorMessage =
                    "Please select a patient first.";

                return;
            }

            if (!$scope.selectedFile) {

                $scope.errorMessage =
                    "Please select an ultrasound image.";

                return;
            }

            $scope.uploading = true;

            ApiService.uploadUltrasound(

                $scope.selectedFile,

                $scope.selectedPatientId

            )
            .then(function (data) {

                $scope.uploadResponse =
                    data;

                $scope.successMessage =
                    "Ultrasound image uploaded successfully.";

            })
            .catch(function (error) {

                console.error(
                    "Ultrasound upload error:",
                    error
                );

                $scope.errorMessage =
                    error && error.message
                        ? error.message
                        : "Ultrasound upload failed.";

            })
            .finally(function () {

                $scope.uploading = false;
            });
        };


        // =========================================================
        // RUN ULTRASOUND AI
        // =========================================================

        $scope.runUltrasoundAI = function () {

            $scope.errorMessage = "";
            $scope.successMessage = "";

            if (!$scope.selectedPatientId) {

                $scope.errorMessage =
                    "Please select a patient first.";

                return;
            }

            if (!$scope.selectedFile) {

                $scope.errorMessage =
                    "Please select an ultrasound image first.";

                return;
            }

            $scope.analyzing = true;

            var payload = {

                patient_id:
                    Number(
                        $scope.selectedPatientId
                    ),

                file_name:
                    $scope.selectedFile.name,

                file_type:
                    $scope.selectedFile.type,

                file_size:
                    $scope.selectedFile.size
            };

            ApiService.runUltrasoundAI(
                payload
            )
            .then(function (data) {

                $scope.ultrasoundResult =
                    data;

                $scope.ultrasoundEvidence =
                    data.ultrasound_evidence ||
                    data.segmentation ||
                    data.evidence ||
                    data;

                $scope.requiresDoctorReview =
                    true;

                $scope.successMessage =
                    "Ultrasound AI analysis completed. "
                    + "Doctor review is required.";

            })
            .catch(function (error) {

                console.error(
                    "Ultrasound AI error:",
                    error
                );

                $scope.errorMessage =
                    error && error.message
                        ? error.message
                        : "Ultrasound AI analysis failed.";

            })
            .finally(function () {

                $scope.analyzing = false;
            });
        };


        // =========================================================
        // MULTIMODAL INTEGRATION
        // =========================================================

        $scope.runMultimodalAI = function () {

            $scope.errorMessage = "";
            $scope.successMessage = "";

            if (!$scope.selectedPatientId) {

                $scope.errorMessage =
                    "Please select a patient first.";

                return;
            }

            if (
                !$scope.clinicalResult &&
                !$scope.ultrasoundResult
            ) {

                $scope.errorMessage =
                    "Run at least one analysis before multimodal integration.";

                return;
            }

            $scope.analyzing = true;

            var payload = {

                patient_id:
                    Number(
                        $scope.selectedPatientId
                    ),

                clinical_result:
                    $scope.clinicalResult,

                ultrasound_result:
                    $scope.ultrasoundResult
            };

            ApiService.runMultimodalAI(
                payload
            )
            .then(function (data) {

                $scope.multimodalResult =
                    data;

                $scope.requiresDoctorReview =
                    true;

                $scope.successMessage =
                    "Multimodal evidence integration completed. "
                    + "Senior Doctor review is required.";

            })
            .catch(function (error) {

                console.error(
                    "Multimodal AI error:",
                    error
                );

                $scope.errorMessage =
                    error && error.message
                        ? error.message
                        : "Multimodal analysis failed.";

            })
            .finally(function () {

                $scope.analyzing = false;
            });
        };


        // =========================================================
        // OPEN PATIENT
        // =========================================================

        $scope.openPatient = function () {

            if (!$scope.selectedPatientId) {
                return;
            }

            $location.path(
                "/patients/" +
                $scope.selectedPatientId
            );
        };


        // =========================================================
        // OPEN WORKFLOW
        // =========================================================

        $scope.openWorkflow = function () {

            if (!$scope.selectedPatientId) {
                return;
            }

            $location.path(
                "/workflow/" +
                $scope.selectedPatientId
            );
        };


        // =========================================================
        // OPEN REPORT
        // =========================================================

        $scope.openReport = function () {

            if (!$scope.selectedPatientId) {
                return;
            }

            $location.path(
                "/reports/" +
                $scope.selectedPatientId
            );
        };


        // =========================================================
        // LOGOUT
        // =========================================================

        $scope.logout = function () {

            AuthService.logout();
        };


        // =========================================================
        // CONFIDENCE FORMAT
        // =========================================================

        $scope.formatConfidence = function (value) {

            if (
                value === null ||
                value === undefined ||
                value === ""
            ) {
                return "N/A";
            }

            var number =
                Number(value);

            if (isNaN(number)) {

                return String(value);
            }

            if (number <= 1) {

                return (
                    number * 100
                ).toFixed(1) + "%";
            }

            return number.toFixed(1) + "%";
        };


        // =========================================================
        // SAFETY MESSAGE
        // =========================================================

        $scope.getReviewMessage = function () {

            return "AI output is clinical decision support only. "
                + "The Senior/Treating Doctor remains the final "
                + "treatment decision authority.";
        };


        // =========================================================
        // INITIAL LOAD
        // =========================================================

        $scope.initialize();

    }

})();