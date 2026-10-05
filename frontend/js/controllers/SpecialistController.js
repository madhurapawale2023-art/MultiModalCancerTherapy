(function () {
    "use strict";

    angular
        .module("MultiModalCancerTherapy")
        .controller("SpecialistController", SpecialistController);

    SpecialistController.$inject = [
        "$scope",
        "$location",
        "ApiService",
        "AuthService"
    ];

    function SpecialistController(
        $scope,
        $location,
        ApiService,
        AuthService
    ) {

        // =========================================================
        // INITIAL STATE
        // =========================================================

        $scope.loading = false;
        $scope.submitting = false;

        $scope.errorMessage = "";
        $scope.successMessage = "";

        $scope.currentUser =
            AuthService.getCurrentUser();

        $scope.patients = [];
        $scope.specialists = [];
        $scope.opinions = [];

        $scope.searchText = "";

        $scope.selectedPatientId = "";
        $scope.selectedSpecialistId = "";

        $scope.opinionForm = {
            patient_id: "",
            specialist_id: "",
            opinion: "",
            recommendation: "",
            notes: ""
        };

        // =========================================================
        // PERMISSIONS
        // =========================================================

        $scope.canSubmitOpinion = AuthService.hasAnyRole([
            "Admin",
            "Senior Doctor",
            "Assistant Doctor",
            "Pathologist",
            "Radiologist",
            "Lab Staff"
        ]);

        // =========================================================
        // INITIALIZE
        // =========================================================

        $scope.initialize = function () {

            $scope.loading = true;

            Promise.all([
                loadPatients(),
                loadSpecialists()
            ])
            .then(function () {
                loadOpinions();
            })
            .catch(function (error) {

                console.error(
                    "Specialist page initialization error:",
                    error
                );

                $scope.errorMessage =
                    error && error.message
                        ? error.message
                        : "Unable to load specialist information.";

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
                }
                else if (
                    data &&
                    Array.isArray(data.items)
                ) {
                    $scope.patients = data.items;
                }
                else {
                    $scope.patients = [];
                }

                var patientId =
                    $location.search().patientId;

                if (patientId) {

                    $scope.selectedPatientId =
                        patientId;

                    $scope.opinionForm.patient_id =
                        patientId;
                }

                return data;
            });
        }

        // =========================================================
        // LOAD SPECIALISTS
        // =========================================================

        function loadSpecialists() {

            return ApiService.getSpecialists()
                .then(function (data) {

                    if (Array.isArray(data)) {
                        $scope.specialists = data;
                    }
                    else if (
                        data &&
                        Array.isArray(data.items)
                    ) {
                        $scope.specialists = data.items;
                    }
                    else {
                        $scope.specialists = [];
                    }

                    return data;
                })
                .catch(function (error) {

                    console.warn(
                        "Specialist list error:",
                        error
                    );

                    $scope.specialists = [];

                    throw error;
                });
        }

        // =========================================================
        // LOAD OPINIONS
        // =========================================================

        function loadOpinions() {

            var params = {};

            if ($scope.selectedPatientId) {
                params.patient_id =
                    $scope.selectedPatientId;
            }

            return ApiService.getSpecialists(params)
                .then(function (data) {

                    /*
                     * Backend specialist endpoint may return
                     * specialist data or opinion history depending
                     * on the implementation.
                     */
                    if (
                        data &&
                        Array.isArray(data.opinions)
                    ) {
                        $scope.opinions =
                            data.opinions;
                    }
                    else if (
                        data &&
                        Array.isArray(data.history)
                    ) {
                        $scope.opinions =
                            data.history;
                    }
                    else {
                        $scope.opinions = [];
                    }

                    return data;
                })
                .catch(function () {

                    $scope.opinions = [];

                    return null;
                });
        }

        // =========================================================
        // PATIENT CHANGE
        // =========================================================

        $scope.onPatientChange = function () {

            $scope.errorMessage = "";
            $scope.successMessage = "";

            $scope.opinionForm.patient_id =
                $scope.selectedPatientId;

            if ($scope.selectedPatientId) {

                $location.search(
                    "patientId",
                    $scope.selectedPatientId
                );

            } else {

                $location.search(
                    "patientId",
                    null
                );
            }

            loadOpinions();
        };

        // =========================================================
        // SPECIALIST CHANGE
        // =========================================================

        $scope.onSpecialistChange = function () {

            $scope.opinionForm.specialist_id =
                $scope.selectedSpecialistId;
        };

        // =========================================================
        // SEARCH SPECIALISTS
        // =========================================================

        $scope.filteredSpecialists = function () {

            var query =
                String($scope.searchText || "")
                    .trim()
                    .toLowerCase();

            if (!query) {
                return $scope.specialists;
            }

            return $scope.specialists.filter(
                function (specialist) {

                    var values = [
                        specialist.full_name,
                        specialist.username,
                        specialist.role,
                        specialist.role_name,
                        specialist.specialization,
                        specialist.email
                    ];

                    return values.some(
                        function (value) {

                            return String(value || "")
                                .toLowerCase()
                                .indexOf(query) !== -1;
                        }
                    );
                }
            );
        };

        // =========================================================
        // SELECT SPECIALIST
        // =========================================================

        $scope.selectSpecialist = function (specialist) {

            if (!specialist) {
                return;
            }

            $scope.selectedSpecialistId =
                specialist.id;

            $scope.opinionForm.specialist_id =
                specialist.id;
        };

        // =========================================================
        // SUBMIT OPINION
        // =========================================================

        $scope.submitOpinion = function (form) {

            if ($scope.submitting) {
                return;
            }

            $scope.errorMessage = "";
            $scope.successMessage = "";

            if (!$scope.canSubmitOpinion) {

                $scope.errorMessage =
                    "You do not have permission to submit specialist opinions.";

                return;
            }

            if (form && form.$invalid) {

                $scope.errorMessage =
                    "Please complete all required fields.";

                return;
            }

            var patientId =
                $scope.opinionForm.patient_id ||
                $scope.selectedPatientId;

            if (!patientId) {

                $scope.errorMessage =
                    "Please select a patient.";

                return;
            }

            if (!$scope.opinionForm.opinion.trim()) {

                $scope.errorMessage =
                    "Please enter the specialist opinion.";

                return;
            }

            var payload = {
                patient_id: Number(patientId),

                specialist_id:
                    $scope.opinionForm.specialist_id
                        ? Number(
                            $scope.opinionForm.specialist_id
                        )
                        : null,

                opinion:
                    $scope.opinionForm.opinion.trim(),

                recommendation:
                    (
                        $scope.opinionForm.recommendation ||
                        ""
                    ).trim(),

                notes:
                    (
                        $scope.opinionForm.notes ||
                        ""
                    ).trim()
            };

            $scope.submitting = true;

            ApiService.submitSpecialistOpinion(payload)
                .then(function () {

                    $scope.successMessage =
                        "Specialist opinion submitted successfully.";

                    $scope.opinionForm.opinion = "";
                    $scope.opinionForm.recommendation = "";
                    $scope.opinionForm.notes = "";

                    return loadOpinions();
                })
                .catch(function (error) {

                    console.error(
                        "Specialist opinion error:",
                        error
                    );

                    $scope.errorMessage =
                        error && error.message
                            ? error.message
                            : "Unable to submit specialist opinion.";

                })
                .finally(function () {

                    $scope.submitting = false;
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
        // CLEAR SEARCH
        // =========================================================

        $scope.clearSearch = function () {
            $scope.searchText = "";
        };

        // =========================================================
        // FORMAT SPECIALIST NAME
        // =========================================================

        $scope.getSpecialistName = function (specialist) {

            if (!specialist) {
                return "Specialist";
            }

            return (
                specialist.full_name ||
                specialist.username ||
                "Specialist"
            );
        };

        // =========================================================
        // FORMAT ROLE
        // =========================================================

        $scope.getSpecialistRole = function (specialist) {

            if (!specialist) {
                return "";
            }

            return (
                specialist.role ||
                specialist.role_name ||
                specialist.specialization ||
                ""
            );
        };

        // =========================================================
        // REFRESH
        // =========================================================

        $scope.refresh = function () {

            $scope.initialize();
        };

        // =========================================================
        // INITIAL LOAD
        // =========================================================

        $scope.initialize();
    }

})();