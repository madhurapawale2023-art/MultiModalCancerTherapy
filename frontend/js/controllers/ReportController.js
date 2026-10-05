(function () {
    "use strict";

    angular
        .module("MultiModalCancerTherapy")
        .controller("ReportController", ReportController);

    ReportController.$inject = [
        "$scope",
        "$routeParams",
        "$location",
        "ApiService",
        "AuthService"
    ];

    function ReportController(
        $scope,
        $routeParams,
        $location,
        ApiService,
        AuthService
    ) {

        // =========================================================
        // INITIAL STATE
        // =========================================================

        $scope.loading = false;
        $scope.errorMessage = "";
        $scope.successMessage = "";

        $scope.currentUser = AuthService.getCurrentUser();

        $scope.patients = [];
        $scope.selectedPatientId =
            $routeParams.patientId ||
            $location.search().patientId ||
            "";

        $scope.selectedPatient = null;

        // Report data
        $scope.report = null;

        $scope.clinicalReport = null;
        $scope.ultrasoundReport = null;
        $scope.aiAnalysis = null;
        $scope.recommendation = null;

        $scope.reportReady = false;


        // =========================================================
        // LOAD PAGE
        // =========================================================

        $scope.initialize = function () {

            $scope.loading = true;
            $scope.errorMessage = "";

            loadPatients()
                .then(function () {

                    if ($scope.selectedPatientId) {
                        return loadPatientReport(
                            $scope.selectedPatientId
                        );
                    }

                    return null;
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

                selectCurrentPatient();

                return data;
            })
            .catch(function (error) {

                console.error(
                    "Report patient loading error:",
                    error
                );

                $scope.errorMessage =
                    error && error.message
                        ? error.message
                        : "Unable to load patients.";

                $scope.patients = [];
            });
        }


        // =========================================================
        // SELECT CURRENT PATIENT
        // =========================================================

        function selectCurrentPatient() {

            if (!$scope.selectedPatientId) {
                return;
            }

            var patient = $scope.patients.find(function (item) {

                return String(item.id) ===
                    String($scope.selectedPatientId);

            });

            if (patient) {
                $scope.selectedPatient = patient;
            }
        }


        // =========================================================
        // PATIENT CHANGE
        // =========================================================

        $scope.onPatientChange = function () {

            $scope.errorMessage = "";
            $scope.successMessage = "";

            clearReport();

            if (!$scope.selectedPatientId) {
                $location.search("patientId", null);
                return;
            }

            selectCurrentPatient();

            $location.search(
                "patientId",
                $scope.selectedPatientId
            );

            loadPatientReport(
                $scope.selectedPatientId
            );
        };


        // =========================================================
        // LOAD REPORT
        // =========================================================

        function loadPatientReport(patientId) {

            if (!patientId) {
                return;
            }

            $scope.loading = true;
            $scope.errorMessage = "";

            return ApiService.getPatientReport(patientId)
                .then(function (data) {

                    $scope.report = data;

                    processReport(data);

                    $scope.reportReady = true;

                    return data;
                })
                .catch(function (error) {

                    console.error(
                        "Patient report loading error:",
                        error
                    );

                    clearReport();

                    $scope.errorMessage =
                        error && error.message
                            ? error.message
                            : "Unable to load patient report.";

                })
                .finally(function () {

                    $scope.loading = false;
                });
        }


        // =========================================================
        // PROCESS REPORT
        // =========================================================

        function processReport(data) {

            if (!data) {
                return;
            }

            $scope.clinicalReport =
                data.clinical ||
                data.clinical_record ||
                data.clinical_data ||
                null;

            $scope.ultrasoundReport =
                data.ultrasound ||
                data.ultrasound_evidence ||
                data.imaging ||
                null;

            $scope.aiAnalysis =
                data.ai_analysis ||
                data.analysis ||
                data.latest_analysis ||
                null;

            $scope.recommendation =
                data.recommendation ||
                data.ai_recommendation ||
                null;
        }


        // =========================================================
        // CLEAR REPORT
        // =========================================================

        function clearReport() {

            $scope.report = null;
            $scope.clinicalReport = null;
            $scope.ultrasoundReport = null;
            $scope.aiAnalysis = null;
            $scope.recommendation = null;
            $scope.reportReady = false;
        }


        // =========================================================
        // REFRESH
        // =========================================================

        $scope.refreshReport = function () {

            if (!$scope.selectedPatientId) {

                $scope.errorMessage =
                    "Please select a patient first.";

                return;
            }

            loadPatientReport(
                $scope.selectedPatientId
            );
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
        // OPEN AI ANALYSIS
        // =========================================================

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
        // REPORT PRINT
        // =========================================================

        $scope.printReport = function () {

            if (!$scope.reportReady) {

                $scope.errorMessage =
                    "Please load a patient report first.";

                return;
            }

            window.print();
        };


        // =========================================================
        // DOWNLOAD REPORT
        // =========================================================

        $scope.downloadReport = function () {

            if (!$scope.reportReady) {

                $scope.errorMessage =
                    "Please load a patient report first.";

                return;
            }

            /*
             * The backend currently returns report data.
             * This creates a safe JSON report download from
             * the loaded response without inventing a PDF API.
             */

            try {

                var content =
                    JSON.stringify(
                        $scope.report,
                        null,
                        2
                    );

                var blob = new Blob(
                    [content],
                    {
                        type: "application/json"
                    }
                );

                var url =
                    window.URL.createObjectURL(blob);

                var link =
                    document.createElement("a");

                var patientCode =
                    $scope.getPatientCode();

                link.href = url;

                link.download =
                    "MMCT_Report_" +
                    patientCode +
                    ".json";

                document.body.appendChild(link);

                link.click();

                document.body.removeChild(link);

                window.URL.revokeObjectURL(url);

                $scope.successMessage =
                    "Report downloaded successfully.";

            } catch (error) {

                console.error(
                    "Report download error:",
                    error
                );

                $scope.errorMessage =
                    "Unable to download report.";
            }
        };


        // =========================================================
        // PATIENT DISPLAY
        // =========================================================

        $scope.getPatientName = function () {

            if (!$scope.selectedPatient) {
                return "Patient";
            }

            return (
                $scope.selectedPatient.full_name ||
                $scope.selectedPatient.name ||
                "Unnamed Patient"
            );
        };


        $scope.getPatientCode = function () {

            if (!$scope.selectedPatient) {
                return "NA";
            }

            return (
                $scope.selectedPatient.patient_code ||
                "NA"
            );
        };


        // =========================================================
        // AI REVIEW STATUS
        // =========================================================

        $scope.requiresDoctorReview = function () {

            if (!$scope.aiAnalysis) {
                return true;
            }

            return (
                $scope.aiAnalysis.requires_doctor_review !== false
            );
        };


        // =========================================================
        // CONFIDENCE
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
                return (
                    number * 100
                ).toFixed(1) + "%";
            }

            return number.toFixed(1) + "%";
        };


        // =========================================================
        // DATA AVAILABILITY
        // =========================================================

        $scope.hasClinicalReport = function () {
            return !!$scope.clinicalReport;
        };

        $scope.hasUltrasoundReport = function () {
            return !!$scope.ultrasoundReport;
        };

        $scope.hasAIAnalysis = function () {
            return !!$scope.aiAnalysis;
        };

        $scope.hasRecommendation = function () {
            return !!$scope.recommendation;
        };


        // =========================================================
        // SAFETY MESSAGE
        // =========================================================

        $scope.getSafetyMessage = function () {

            return "AI-generated information is clinical "
                + "decision support only. The Senior/Treating "
                + "Doctor remains the final treatment decision authority.";
        };


        // =========================================================
        // INITIALIZE
        // =========================================================

        $scope.initialize();
    }

})();