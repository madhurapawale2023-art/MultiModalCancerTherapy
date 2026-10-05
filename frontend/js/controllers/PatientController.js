(function () {
    "use strict";

    angular
        .module("MultiModalCancerTherapy")
        .controller("PatientController", PatientController);

    PatientController.$inject = [
        "$scope",
        "$location",
        "$route",
        "$q",
        "ApiService",
        "AuthService"
    ];

    function PatientController(
        $scope,
        $location,
        $route,
        $q,
        ApiService,
        AuthService
    ) {

        // =========================================================
        // STATE
        // =========================================================

        $scope.loading = false;
        $scope.saving = false;
        $scope.errorMessage = "";
        $scope.successMessage = "";

        $scope.searchText = "";

        $scope.patients = [];
        $scope.totalPatients = 0;

        $scope.currentUser = AuthService.getCurrentUser();

        $scope.canManagePatients =
            AuthService.hasAnyRole([
                "Admin",
                "Senior Doctor",
                "Assistant Doctor"
            ]);

        // Modal state
        $scope.showPatientModal = false;
        $scope.editMode = false;

        $scope.patientForm = {
            id: null,
            patient_code: "",
            full_name: "",
            age: null,
            sex: "",
            phone: "",
            email: "",
            address: "",
            diagnosis: "",
            clinical_notes: "",
            status: "Registered"
        };


        // =========================================================
        // LOAD PATIENTS
        // =========================================================

        $scope.loadPatients = function () {

            $scope.loading = true;
            $scope.errorMessage = "";
            $scope.successMessage = "";

            return ApiService.getPatients({
                page: 1,
                page_size: 100
            })
            .then(function (data) {

                if (Array.isArray(data)) {
                    $scope.patients = data;
                    $scope.totalPatients = data.length;
                }
                else if (data && Array.isArray(data.items)) {
                    $scope.patients = data.items;
                    $scope.totalPatients =
                        angular.isNumber(data.total)
                            ? data.total
                            : data.items.length;
                }
                else {
                    $scope.patients = [];
                    $scope.totalPatients = 0;
                }

            })
            .catch(function (error) {

                console.error(
                    "Patient loading error:",
                    error
                );

                $scope.errorMessage =
                    error && error.message
                        ? error.message
                        : "Unable to load patient records.";

            })
            .finally(function () {

                $scope.loading = false;
            });
        };


        // =========================================================
        // REFRESH
        // =========================================================

        $scope.refreshPatients = function () {
            $scope.loadPatients();
        };


        // =========================================================
        // SEARCH / FILTER
        // =========================================================

        $scope.filteredPatients = function () {

            var search =
                String($scope.searchText || "")
                    .trim()
                    .toLowerCase();

            if (!search) {
                return $scope.patients;
            }

            return $scope.patients.filter(function (patient) {

                var values = [
                    patient.patient_code,
                    patient.full_name,
                    patient.name,
                    patient.age,
                    patient.sex,
                    patient.status,
                    patient.workflow_status,
                    patient.diagnosis
                ];

                return values.some(function (value) {

                    return String(value || "")
                        .toLowerCase()
                        .indexOf(search) !== -1;

                });
            });
        };


        // =========================================================
        // OPEN REGISTER MODAL
        // =========================================================

        $scope.openRegisterModal = function () {

            if (!$scope.canManagePatients) {
                $scope.errorMessage =
                    "You do not have permission to register a patient.";
                return;
            }

            $scope.editMode = false;

            $scope.patientForm = {
                id: null,
                patient_code: "",
                full_name: "",
                age: null,
                sex: "",
                phone: "",
                email: "",
                address: "",
                diagnosis: "",
                clinical_notes: "",
                status: "Registered"
            };

            $scope.errorMessage = "";
            $scope.successMessage = "";
            $scope.showPatientModal = true;
        };


        // =========================================================
        // OPEN EDIT MODAL
        // =========================================================

        $scope.openEditModal = function (patient) {

            if (!$scope.canManagePatients) {
                $scope.errorMessage =
                    "You do not have permission to edit patient records.";
                return;
            }

            if (!patient) {
                return;
            }

            $scope.editMode = true;

            $scope.patientForm = angular.copy(patient);

            // Support backend naming variations
            if (!$scope.patientForm.full_name) {
                $scope.patientForm.full_name =
                    patient.name || "";
            }

            $scope.errorMessage = "";
            $scope.successMessage = "";
            $scope.showPatientModal = true;
        };


        // =========================================================
        // CLOSE MODAL
        // =========================================================

        $scope.closePatientModal = function () {

            if ($scope.saving) {
                return;
            }

            $scope.showPatientModal = false;
            $scope.errorMessage = "";
        };


        // =========================================================
        // SAVE PATIENT
        // =========================================================

        $scope.savePatient = function (form) {

            if ($scope.saving) {
                return;
            }

            $scope.errorMessage = "";
            $scope.successMessage = "";

            if (form && form.$invalid) {

                $scope.errorMessage =
                    "Please complete all required patient fields.";

                return;
            }

            var payload = {
                full_name: ($scope.patientForm.full_name || "").trim(),
                age: $scope.patientForm.age,
                sex: $scope.patientForm.sex,
                phone: ($scope.patientForm.phone || "").trim(),
                email: ($scope.patientForm.email || "").trim(),
                address: ($scope.patientForm.address || "").trim(),
                diagnosis: ($scope.patientForm.diagnosis || "").trim(),
                clinical_notes:
                    ($scope.patientForm.clinical_notes || "").trim(),
                status:
                    $scope.patientForm.status || "Registered"
            };

            if (!payload.full_name) {

                $scope.errorMessage =
                    "Patient name is required.";

                return;
            }

            if (!payload.age) {

                $scope.errorMessage =
                    "Patient age is required.";

                return;
            }

            if (!payload.sex) {

                $scope.errorMessage =
                    "Please select patient sex.";

                return;
            }

            $scope.saving = true;

            var action;

            if ($scope.editMode && $scope.patientForm.id) {

                action = ApiService.updatePatient(
                    $scope.patientForm.id,
                    payload
                );

            } else {

                action = ApiService.createPatient(
                    payload
                );
            }

            action
                .then(function () {

                    $scope.successMessage =
                        $scope.editMode
                            ? "Patient updated successfully."
                            : "Patient registered successfully.";

                    $scope.showPatientModal = false;

                    return $scope.loadPatients();
                })
                .catch(function (error) {

                    console.error(
                        "Patient save error:",
                        error
                    );

                    $scope.errorMessage =
                        error && error.message
                            ? error.message
                            : "Unable to save patient record.";
                })
                .finally(function () {

                    $scope.saving = false;
                });
        };


        // =========================================================
        // VIEW PATIENT
        // =========================================================

        $scope.viewPatient = function (patient) {

            if (!patient || !patient.id) {
                return;
            }

            $location.path(
                "/patients/" + patient.id
            );
        };


        // =========================================================
        // DELETE PATIENT
        // =========================================================

        $scope.deletePatient = function (patient) {

            if (!$scope.canManagePatients) {
                $scope.errorMessage =
                    "You do not have permission to delete patient records.";
                return;
            }

            if (!patient || !patient.id) {
                return;
            }

            var name =
                patient.full_name ||
                patient.name ||
                patient.patient_code ||
                "this patient";

            var confirmed = window.confirm(
                "Are you sure you want to delete " +
                name +
                "?"
            );

            if (!confirmed) {
                return;
            }

            $scope.loading = true;
            $scope.errorMessage = "";
            $scope.successMessage = "";

            ApiService.deletePatient(patient.id)
                .then(function () {

                    $scope.successMessage =
                        "Patient deleted successfully.";

                    return $scope.loadPatients();
                })
                .catch(function (error) {

                    console.error(
                        "Patient delete error:",
                        error
                    );

                    $scope.errorMessage =
                        error && error.message
                            ? error.message
                            : "Unable to delete patient record.";
                })
                .finally(function () {

                    $scope.loading = false;
                });
        };


        // =========================================================
        // CLEAR SEARCH
        // =========================================================

        $scope.clearSearch = function () {
            $scope.searchText = "";
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
                value.indexOf("approved") !== -1
            ) {
                return "mmct-badge-success";
            }

            if (
                value.indexOf("review") !== -1 ||
                value.indexOf("pending") !== -1
            ) {
                return "mmct-badge-warning";
            }

            if (
                value.indexOf("cancel") !== -1 ||
                value.indexOf("reject") !== -1
            ) {
                return "mmct-badge-danger";
            }

            if (
                value.indexOf("progress") !== -1 ||
                value.indexOf("active") !== -1
            ) {
                return "mmct-badge-primary";
            }

            return "mmct-badge-secondary";
        };


        // =========================================================
        // EMPTY STATE
        // =========================================================

        $scope.hasPatients = function () {
            return $scope.patients.length > 0;
        };


        // =========================================================
        // INITIAL LOAD
        // =========================================================

        $scope.loadPatients();
    }

})();