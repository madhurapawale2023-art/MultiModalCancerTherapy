(function () {
    "use strict";

    angular
        .module("MultiModalCancerTherapy")
        .controller("WorkflowController", WorkflowController);

    WorkflowController.$inject = [
        "$scope",
        "$routeParams",
        "$location",
        "$q",
        "ApiService",
        "AuthService"
    ];

    function WorkflowController(
        $scope,
        $routeParams,
        $location,
        $q,
        ApiService,
        AuthService
    ) {

        // =========================================================
        // INITIAL STATE
        // =========================================================

        $scope.loading = false;
        $scope.updating = false;

        $scope.errorMessage = "";
        $scope.successMessage = "";

        $scope.currentUser =
            AuthService.getCurrentUser();

        $scope.patients = [];

        $scope.selectedPatientId =
            $routeParams.patientId ||
            $location.search().patientId ||
            "";

        $scope.selectedPatient = null;

        $scope.workflow = null;
        $scope.progress = null;
        $scope.history = [];

        $scope.workflowStatuses = [];

        // =========================================================
        // 11-STEP CLINICAL WORKFLOW
        // =========================================================

        $scope.steps = [
            {
                number: 1,
                title: "Patient Registration",
                description: "Register patient and create clinical record."
            },
            {
                number: 2,
                title: "Clinical Data",
                description: "Capture patient demographics and clinical information."
            },
            {
                number: 3,
                title: "Laboratory Review",
                description: "Review relevant laboratory findings."
            },
            {
                number: 4,
                title: "Pathology Review",
                description: "Review pathology evidence when available."
            },
            {
                number: 5,
                title: "Ultrasound / Imaging",
                description: "Review ultrasound or imaging evidence."
            },
            {
                number: 6,
                title: "AI Clinical Analysis",
                description: "Generate clinical decision-support analysis."
            },
            {
                number: 7,
                title: "Multimodal Evidence",
                description: "Integrate available multimodal evidence."
            },
            {
                number: 8,
                title: "Specialist Review",
                description: "Obtain relevant specialist input."
            },
            {
                number: 9,
                title: "Treatment Planning",
                description: "Prepare treatment planning evidence."
            },
            {
                number: 10,
                title: "Senior Doctor Review",
                description: "Senior/Treating Doctor reviews AI-supported evidence."
            },
            {
                number: 11,
                title: "Final Decision",
                description: "Final treatment decision by the responsible doctor."
            }
        ];

        // =========================================================
        // UPDATE FORM
        // =========================================================

        $scope.updateForm = {
            status: "",
            step_number: null,
            notes: ""
        };

        // =========================================================
        // PERMISSIONS
        // =========================================================

        $scope.canUpdateWorkflow = AuthService.hasAnyRole([
            "Admin",
            "Senior Doctor",
            "Assistant Doctor",
            "Pathologist",
            "Radiologist",
            "Lab Staff"
        ]);

        $scope.canFinalize = AuthService.hasAnyRole([
            "Admin",
            "Senior Doctor"
        ]);


        // =========================================================
        // INITIALIZE
        // =========================================================

        $scope.initialize = function () {

            $scope.loading = true;
            $scope.errorMessage = "";

            $q.all({
                patients: loadPatients(),
                statuses: loadStatuses()
            })
            .then(function (result) {

                processPatients(result.patients);
                processStatuses(result.statuses);

                if ($scope.selectedPatientId) {
                    selectCurrentPatient();

                    return loadWorkflowData(
                        $scope.selectedPatientId
                    );
                }

                return null;

            })
            .catch(function (error) {

                console.error(
                    "Workflow initialization error:",
                    error
                );

                $scope.errorMessage =
                    error && error.message
                        ? error.message
                        : "Unable to load workflow information.";
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
                    "Workflow patient loading error:",
                    error
                );

                return {
                    items: []
                };
            });
        }

        function processPatients(data) {

            if (Array.isArray(data)) {

                $scope.patients = data;

            } else if (
                data &&
                Array.isArray(data.items)
            ) {

                $scope.patients = data.items;

            } else {

                $scope.patients = [];
            }
        }


        // =========================================================
        // LOAD WORKFLOW STATUSES
        // =========================================================

        function loadStatuses() {

            return ApiService.getWorkflowStatuses()
                .then(function (data) {
                    return data;
                })
                .catch(function (error) {

                    console.warn(
                        "Workflow status loading error:",
                        error
                    );

                    return [];
                });
        }

        function processStatuses(data) {

            if (Array.isArray(data)) {

                $scope.workflowStatuses = data;

            } else if (
                data &&
                Array.isArray(data.items)
            ) {

                $scope.workflowStatuses = data.items;

            } else if (
                data &&
                Array.isArray(data.statuses)
            ) {

                $scope.workflowStatuses =
                    data.statuses;

            } else {

                $scope.workflowStatuses = [];
            }
        }


        // =========================================================
        // SELECT PATIENT
        // =========================================================

        function selectCurrentPatient() {

            if (!$scope.selectedPatientId) {
                return;
            }

            var patient =
                $scope.patients.find(function (item) {

                    return String(item.id) ===
                        String($scope.selectedPatientId);

                });

            if (patient) {

                $scope.selectedPatient =
                    patient;
            }
        }


        // =========================================================
        // PATIENT CHANGE
        // =========================================================

        $scope.onPatientChange = function () {

            $scope.errorMessage = "";
            $scope.successMessage = "";

            clearWorkflowData();

            if (!$scope.selectedPatientId) {

                $location.search(
                    "patientId",
                    null
                );

                return;
            }

            selectCurrentPatient();

            $location.search(
                "patientId",
                $scope.selectedPatientId
            );

            loadWorkflowData(
                $scope.selectedPatientId
            );
        };


        // =========================================================
        // LOAD WORKFLOW DATA
        // =========================================================

        function loadWorkflowData(patientId) {

            if (!patientId) {
                return;
            }

            $scope.loading = true;

            return $q.all({
                workflow:
                    ApiService.getWorkflow(patientId),

                progress:
                    ApiService.getWorkflowProgress(patientId)
                        .catch(function () {
                            return null;
                        }),

                history:
                    ApiService.getWorkflowHistory(patientId)
                        .catch(function () {
                            return [];
                        })
            })
            .then(function (result) {

                $scope.workflow =
                    result.workflow;

                $scope.progress =
                    result.progress;

                processHistory(
                    result.history
                );

                processWorkflow();
            })
            .catch(function (error) {

                console.error(
                    "Workflow loading error:",
                    error
                );

                $scope.errorMessage =
                    error && error.message
                        ? error.message
                        : "Unable to load patient workflow.";
            })
            .finally(function () {

                $scope.loading = false;
            });
        }


        // =========================================================
        // PROCESS HISTORY
        // =========================================================

        function processHistory(data) {

            if (Array.isArray(data)) {

                $scope.history = data;

            } else if (
                data &&
                Array.isArray(data.items)
            ) {

                $scope.history = data.items;

            } else if (
                data &&
                Array.isArray(data.history)
            ) {

                $scope.history = data.history;

            } else {

                $scope.history = [];
            }
        }


        // =========================================================
        // PROCESS WORKFLOW
        // =========================================================

        function processWorkflow() {

            if (!$scope.workflow) {
                return;
            }

            $scope.updateForm.status =
                $scope.workflow.workflow_status ||
                $scope.workflow.status ||
                "";

            $scope.updateForm.step_number =
                Number(
                    $scope.workflow.current_step ||
                    $scope.workflow.step_number ||
                    $scope.workflow.current_step_number ||
                    1
                );

            if (
                !$scope.updateForm.step_number ||
                $scope.updateForm.step_number < 1
            ) {
                $scope.updateForm.step_number = 1;
            }

            if (
                $scope.updateForm.step_number >
                $scope.steps.length
            ) {
                $scope.updateForm.step_number =
                    $scope.steps.length;
            }
        }


        // =========================================================
        // GET CURRENT STEP
        // =========================================================

        $scope.getCurrentStep = function () {

            var step =
                Number(
                    $scope.updateForm.step_number || 1
                );

            return step;
        };


        // =========================================================
        // STEP STATUS
        // =========================================================

        $scope.getStepState = function (stepNumber) {

            var current =
                $scope.getCurrentStep();

            if (stepNumber < current) {
                return "completed";
            }

            if (stepNumber === current) {
                return "active";
            }

            return "pending";
        };


        // =========================================================
        // STEP CSS CLASS
        // =========================================================

        $scope.getStepClass = function (stepNumber) {

            return (
                "mmct-workflow-step " +
                $scope.getStepState(stepNumber)
            );
        };


        // =========================================================
        // PROGRESS PERCENTAGE
        // =========================================================

        $scope.getProgressPercentage = function () {

            if (
                $scope.progress &&
                angular.isNumber(
                    $scope.progress.progress_percentage
                )
            ) {
                return $scope.progress.progress_percentage;
            }

            if (
                $scope.progress &&
                angular.isNumber(
                    $scope.progress.percentage
                )
            ) {
                return $scope.progress.percentage;
            }

            var current =
                $scope.getCurrentStep();

            return Math.round(
                (
                    current /
                    $scope.steps.length
                ) * 100
            );
        };


        // =========================================================
        // STATUS CLASS
        // =========================================================

        $scope.getStatusClass = function (status) {

            var value =
                String(status || "")
                    .toLowerCase();

            if (
                value.indexOf("complete") !== -1 ||
                value.indexOf("approved") !== -1 ||
                value.indexOf("final") !== -1
            ) {
                return "mmct-badge-success";
            }

            if (
                value.indexOf("pending") !== -1 ||
                value.indexOf("review") !== -1
            ) {
                return "mmct-badge-warning";
            }

            if (
                value.indexOf("reject") !== -1 ||
                value.indexOf("cancel") !== -1
            ) {
                return "mmct-badge-danger";
            }

            if (
                value.indexOf("active") !== -1 ||
                value.indexOf("progress") !== -1
            ) {
                return "mmct-badge-primary";
            }

            return "mmct-badge-secondary";
        };


        // =========================================================
        // UPDATE WORKFLOW
        // =========================================================

        $scope.updateWorkflow = function (form) {

            if ($scope.updating) {
                return;
            }

            $scope.errorMessage = "";
            $scope.successMessage = "";

            if (!$scope.selectedPatientId) {

                $scope.errorMessage =
                    "Please select a patient first.";

                return;
            }

            if (!$scope.canUpdateWorkflow) {

                $scope.errorMessage =
                    "You do not have permission to update workflow.";

                return;
            }

            if (form && form.$invalid) {

                $scope.errorMessage =
                    "Please complete the workflow update fields.";

                return;
            }

            var stepNumber =
                Number(
                    $scope.updateForm.step_number
                );

            if (
                !stepNumber ||
                stepNumber < 1 ||
                stepNumber > $scope.steps.length
            ) {

                $scope.errorMessage =
                    "Please select a valid workflow step.";

                return;
            }

            var payload = {
                status:
                    $scope.updateForm.status || null,

                step_number:
                    stepNumber,

                notes:
                    (
                        $scope.updateForm.notes ||
                        ""
                    ).trim()
            };

            /*
             * Final step is intentionally restricted to
             * Admin / Senior Doctor.
             */
            if (
                stepNumber === 11 &&
                !$scope.canFinalize
            ) {

                $scope.errorMessage =
                    "Final decision workflow step requires Senior Doctor or Admin authority.";

                return;
            }

            $scope.updating = true;

            ApiService.updateWorkflow(
                $scope.selectedPatientId,
                payload
            )
            .then(function (data) {

                $scope.workflow = data;

                $scope.successMessage =
                    "Workflow updated successfully.";

                $scope.updateForm.notes = "";

                return loadWorkflowData(
                    $scope.selectedPatientId
                );
            })
            .catch(function (error) {

                console.error(
                    "Workflow update error:",
                    error
                );

                $scope.errorMessage =
                    error && error.message
                        ? error.message
                        : "Unable to update workflow.";
            })
            .finally(function () {

                $scope.updating = false;
            });
        };


        // =========================================================
        // REFRESH
        // =========================================================

        $scope.refreshWorkflow = function () {

            if (!$scope.selectedPatientId) {

                $scope.errorMessage =
                    "Please select a patient first.";

                return;
            }

            loadWorkflowData(
                $scope.selectedPatientId
            );
        };


        // =========================================================
        // NAVIGATION
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


        $scope.openAIAnalysis = function () {

            if (!$scope.selectedPatientId) {
                return;
            }

            $location.path("/ai-analysis")
                .search({
                    patientId:
                        $scope.selectedPatientId
                });
        };


        $scope.openReport = function () {

            if (!$scope.selectedPatientId) {
                return;
            }

            $location.path(
                "/reports/" +
                $scope.selectedPatientId
            );
        };


        $scope.openSpecialists = function () {

            $location.path("/specialists")
                .search({
                    patientId:
                        $scope.selectedPatientId
                });
        };


        // =========================================================
        // CLEAR
        // =========================================================

        function clearWorkflowData() {

            $scope.selectedPatient = null;
            $scope.workflow = null;
            $scope.progress = null;
            $scope.history = [];

            $scope.updateForm.status = "";
            $scope.updateForm.step_number = 1;
            $scope.updateForm.notes = "";
        }


        // =========================================================
        // INITIAL LOAD
        // =========================================================

        $scope.initialize();
    }

})();