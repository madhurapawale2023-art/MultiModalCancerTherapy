(function () {
    "use strict";

    angular
        .module("MultiModalCancerTherapy")
        .controller("PatientDetailController", PatientDetailController);

    PatientDetailController.$inject = [
        "$scope",
        "$routeParams",
        "$location",
        "$q",
        "ApiService",
        "AuthService"
    ];

    function PatientDetailController(
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

        $scope.loading = true;
        $scope.errorMessage = "";
        $scope.successMessage = "";

        $scope.patientId = $routeParams.patientId;

        $scope.patient = null;
        $scope.workflow = null;
        $scope.latestAnalysis = null;
        $scope.recommendation = null;

        $scope.clinicalRecord = null;
        $scope.ultrasoundEvidence = [];

        $scope.currentUser = AuthService.getCurrentUser();

        // =========================================================
        // PERMISSIONS
        // =========================================================

        $scope.canEdit = AuthService.hasAnyRole([
            "Admin",
            "Senior Doctor",
            "Assistant Doctor"
        ]);

        $scope.canRunAI = AuthService.hasAnyRole([
            "Admin",
            "Senior Doctor",
            "Assistant Doctor",
            "Radiologist",
            "Pathologist",
            "Lab Staff"
        ]);

        $scope.canReview = AuthService.hasAnyRole([
            "Admin",
            "Senior Doctor"
        ]);

        // =========================================================
        // LOAD PATIENT
        // =========================================================

        $scope.loadPatient = function () {

            if (!$scope.patientId) {

                $scope.errorMessage =
                    "Patient ID is missing.";

                $scope.loading = false;

                return;
            }

            $scope.loading = true;
            $scope.errorMessage = "";

            var patientPromise =
                ApiService.getPatient($scope.patientId);

            var workflowPromise =
                ApiService.getWorkflow($scope.patientId)
                    .catch(function () {
                        return null;
                    });

            var reportPromise =
                ApiService.getPatientReport($scope.patientId)
                    .catch(function () {
                        return null;
                    });

            $q.all({
                patient: patientPromise,
                workflow: workflowPromise,
                report: reportPromise
            })
            .then(function (result) {

                if (!result.patient) {
                    throw {
                        message: "Patient record could not be loaded."
                    };
                }

                $scope.patient = result.patient;

                $scope.workflow = result.workflow;

                processReport(result.report);

            })
            .catch(function (error) {

                console.error(
                    "Patient detail loading error:",
                    error
                );

                $scope.errorMessage =
                    error && error.message
                        ? error.message
                        : "Unable to load patient details.";
            })
            .finally(function () {

                $scope.loading = false;
            });
        };


        // =========================================================
        // PROCESS REPORT / EVIDENCE
        // =========================================================

        function processReport(report) {

            if (!report) {
                return;
            }

            /*
             * Keep compatibility with different report response
             * shapes returned by the backend.
             */

            $scope.clinicalRecord =
                report.clinical ||
                report.clinical_record ||
                null;

            $scope.ultrasoundEvidence =
                report.ultrasound ||
                report.ultrasound_evidence ||
                report.images ||
                [];

            $scope.latestAnalysis =
                report.ai_analysis ||
                report.latest_analysis ||
                null;

            $scope.recommendation =
                report.recommendation ||
                report.ai_recommendation ||
                null;
        }


        // =========================================================
        // REFRESH
        // =========================================================

        $scope.refreshPatient = function () {
            $scope.loadPatient();
        };


        // =========================================================
        // EDIT PATIENT
        // =========================================================

        $scope.editPatient = function () {

            if (!$scope.patient || !$scope.patient.id) {
                return;
            }

            if (!$scope.canEdit) {

                $scope.errorMessage =
                    "You do not have permission to edit this patient.";

                return;
            }

            /*
             * Open patient registry route.
             * PatientController can handle editing.
             */
            $location.path("/patients");
        };


        // =========================================================
        // AI ANALYSIS
        // =========================================================

        $scope.openAIAnalysis = function () {

            if (!$scope.patient || !$scope.patient.id) {
                return;
            }

            if (!$scope.canRunAI) {

                $scope.errorMessage =
                    "You do not have permission to run AI analysis.";

                return;
            }

            $location.path(
                "/ai-analysis"
            )
            .search({
                patientId: $scope.patient.id
            });
        };


        // =========================================================
        // REPORT
        // =========================================================

        $scope.openReport = function () {

            if (!$scope.patient || !$scope.patient.id) {
                return;
            }

            $location.path(
                "/reports/" + $scope.patient.id
            );
        };


        // =========================================================
        // WORKFLOW
        // =========================================================

        $scope.openWorkflow = function () {

            if (!$scope.patient || !$scope.patient.id) {
                return;
            }

            $location.path(
                "/workflow/" + $scope.patient.id
            );
        };


        // =========================================================
        // SPECIALISTS
        // =========================================================

        $scope.openSpecialists = function () {

            if (!$scope.patient || !$scope.patient.id) {
                return;
            }

            $location.path(
                "/specialists"
            );
        };


        // =========================================================
        // PATIENT LIST
        // =========================================================

        $scope.backToPatients = function () {

            $location.path("/patients");
        };


        // =========================================================
        // STATUS
        // =========================================================

        $scope.getStatus = function () {

            if (!$scope.patient) {
                return "Unknown";
            }

            return (
                $scope.patient.workflow_status ||
                $scope.patient.status ||
                "Registered"
            );
        };


        $scope.getStatusClass = function () {

            var status =
                String($scope.getStatus())
                    .toLowerCase();

            if (
                status.indexOf("complete") !== -1 ||
                status.indexOf("approved") !== -1
            ) {
                return "mmct-badge-success";
            }

            if (
                status.indexOf("review") !== -1 ||
                status.indexOf("pending") !== -1
            ) {
                return "mmct-badge-warning";
            }

            if (
                status.indexOf("cancel") !== -1 ||
                status.indexOf("reject") !== -1
            ) {
                return "mmct-badge-danger";
            }

            if (
                status.indexOf("progress") !== -1 ||
                status.indexOf("active") !== -1
            ) {
                return "mmct-badge-primary";
            }

            return "mmct-badge-secondary";
        };


        // =========================================================
        // PATIENT DISPLAY
        // =========================================================

        $scope.getPatientName = function () {

            if (!$scope.patient) {
                return "Patient";
            }

            return (
                $scope.patient.full_name ||
                $scope.patient.name ||
                "Unnamed Patient"
            );
        };


        $scope.getPatientCode = function () {

            if (!$scope.patient) {
                return "";
            }

            return (
                $scope.patient.patient_code ||
                "N/A"
            );
        };


        // =========================================================
        // AI REVIEW STATUS
        // =========================================================

        $scope.requiresDoctorReview = function () {

            if (!$scope.latestAnalysis) {
                return true;
            }

            if (
                $scope.latestAnalysis.requires_doctor_review === false
            ) {
                return false;
            }

            return true;
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

            var number = Number(value);

            if (isNaN(number)) {
                return String(value);
            }

            if (number <= 1) {
                return (number * 100).toFixed(1) + "%";
            }

            return number.toFixed(1) + "%";
        };


        // =========================================================
        // EVIDENCE CHECK
        // =========================================================

        $scope.hasClinicalEvidence = function () {

            return !!$scope.clinicalRecord;
        };


        $scope.hasUltrasoundEvidence = function () {

            return (
                Array.isArray($scope.ultrasoundEvidence) &&
                $scope.ultrasoundEvidence.length > 0
            );
        };


        $scope.hasAIAnalysis = function () {

            return !!$scope.latestAnalysis;
        };


        $scope.hasRecommendation = function () {

            return !!$scope.recommendation;
        };


        // =========================================================
        // INITIAL LOAD
        // =========================================================

        $scope.loadPatient();
    }

})();