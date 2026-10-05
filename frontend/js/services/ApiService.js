(function () {
    "use strict";

    angular
        .module("MultiModalCancerTherapy")
        .factory("ApiService", ApiService);

    ApiService.$inject = ["$http", "$q", "APP_CONFIG"];

    function ApiService($http, $q, APP_CONFIG) {

        var API_BASE =
            (APP_CONFIG && APP_CONFIG.apiBaseUrl) ||
            "http://127.0.0.1:8000";

        // Routes served under /api (auth, ai, audit, dashboard, info)
        var API_URL = API_BASE + "/api";

        // Root-level routes (health, patients, reports, specialists, workflow)
        var API_ROOT = API_BASE;

        var service = {

            // Health / Info
            health: health,
            getHealth: health,
            getAppInfo: getAppInfo,

            // Authentication
            login: login,
            getCurrentUser: getCurrentUser,

            // Patients
            getPatients: getPatients,
            getPatient: getPatient,
            createPatient: createPatient,
            updatePatient: updatePatient,
            deletePatient: deletePatient,

            // AI
            getAIStatus: getAIStatus,
            runClinicalAI: runClinicalAI,
            runUltrasoundAI: runUltrasoundAI,
            runMultimodalAI: runMultimodalAI,
            uploadUltrasound: uploadUltrasound,

            // Reports
            getPatientReport: getPatientReport,

            // Dashboard
            getDashboard: getDashboard,

            // Specialists
            getSpecialists: getSpecialists,
            submitSpecialistOpinion: submitSpecialistOpinion,

            // Workflow
            getWorkflow: getWorkflow,
            updateWorkflow: updateWorkflow,
            getWorkflowProgress: getWorkflowProgress,
            getWorkflowHistory: getWorkflowHistory,
            getWorkflowStatuses: getWorkflowStatuses,

            // Audit
            getAuditLogs: getAuditLogs,
            getMyAuditLogs: getMyAuditLogs,
            createAuditLog: createAuditLog,

            // Generic
            request: request
        };

        return service;


        // =========================================================
        // COMMON REQUEST CONFIG
        // =========================================================

        function getToken() {
            return localStorage.getItem("mmct_access_token");
        }

        function buildConfig(config) {

            config = config || {};

            config.headers = config.headers || {};

            var token = getToken();

            if (token) {
                config.headers.Authorization = "Bearer " + token;
            }

            return config;
        }

        function handleError(error) {

            var status = error && error.status;
            var message = "Request failed.";

            if (error && error.data) {

                if (typeof error.data.detail === "string") {
                    message = error.data.detail;
                } else if (error.data.message) {
                    message = error.data.message;
                }
            }

            switch (status) {

                case 400:
                    message = message || "Invalid request.";
                    break;

                case 401:
                    message = "Authentication required. Please login again.";
                    localStorage.removeItem("mmct_access_token");
                    localStorage.removeItem("mmct_current_user");
                    break;

                case 403:
                    message = "You do not have permission to perform this action.";
                    break;

                case 404:
                    message = "Requested resource was not found.";
                    break;

                case 409:
                    message = "This record already exists or conflicts with another record.";
                    break;

                case 422:
                    message = "Please verify the entered data.";
                    break;

                case 500:
                    message = "Server error. Please try again.";
                    break;

                case -1:
                    message = "Backend server is not reachable.";
                    break;
            }

            return $q.reject({
                status: status,
                message: message,
                data: error ? error.data : null
            });
        }


        // =========================================================
        // GENERIC REQUEST
        // =========================================================

        function request(method, url, data, config) {

            var options = buildConfig(config || {});

            options.method = method;
            options.url = url;

            if (data !== undefined && data !== null) {
                options.data = data;
            }

            return $http(options)
                .then(function (response) {
                    return response.data;
                })
                .catch(handleError);
        }


        // =========================================================
        // HEALTH
        // =========================================================

        function health() {

            return request(
                "GET",
                API_BASE + "/health"
            );
        }


        // =========================================================
        // APPLICATION INFO
        // =========================================================

        function getAppInfo() {

            return request(
                "GET",
                API_BASE + "/api/info"
            );
        }


        // =========================================================
        // AUTH LOGIN
        // =========================================================

        function login(credentials) {

            return request(
                "POST",
                API_URL + "/auth/login",
                {
                    username: credentials.username,
                    password: credentials.password
                }
            );
        }


        // =========================================================
        // CURRENT USER
        // =========================================================

        function getCurrentUser() {

            return request(
                "GET",
                API_URL + "/auth/me"
            );
        }


        // =========================================================
        // PATIENTS
        // =========================================================

        function getPatients(params) {

            return request(
                "GET",
                API_ROOT + "/patients/",
                null,
                {
                    params: params || {}
                }
            );
        }

        function getPatient(patientId) {

            return request(
                "GET",
                API_ROOT + "/patients/" + patientId
            );
        }

        function createPatient(patientData) {

            return request(
                "POST",
                API_ROOT + "/patients/",
                patientData
            );
        }

        function updatePatient(patientId, patientData) {

            return request(
                "PUT",
                API_ROOT + "/patients/" + patientId,
                patientData
            );
        }

        function deletePatient(patientId) {

            return request(
                "DELETE",
                API_ROOT + "/patients/" + patientId
            );
        }


        // =========================================================
        // AI STATUS
        // =========================================================

        function getAIStatus() {

            return request(
                "GET",
                API_URL + "/ai/status"
            );
        }


        // =========================================================
        // CLINICAL AI
        // =========================================================

        function runClinicalAI(payload) {

            return request(
                "POST",
                API_URL + "/ai/clinical",
                payload
            );
        }


        // =========================================================
        // ULTRASOUND AI
        // =========================================================

        function runUltrasoundAI(payload) {

            return request(
                "POST",
                API_URL + "/ai/ultrasound",
                payload
            );
        }


        // =========================================================
        // MULTIMODAL AI
        // =========================================================

        function runMultimodalAI(payload) {

            return request(
                "POST",
                API_URL + "/ai/multimodal",
                payload
            );
        }


        // =========================================================
        // ULTRASOUND FILE UPLOAD
        // =========================================================

        function uploadUltrasound(file, patientId) {

            var formData = new FormData();

            formData.append("file", file);

            if (patientId !== undefined && patientId !== null) {
                formData.append(
                    "patient_id",
                    patientId
                );
            }

            var token = getToken();

            var headers = {
                "Content-Type": undefined
            };

            if (token) {
                headers.Authorization = "Bearer " + token;
            }

            return $http({
                method: "POST",
                url: API_URL + "/ai/ultrasound/upload",
                data: formData,
                headers: headers,
                transformRequest: angular.identity
            })
            .then(function (response) {
                return response.data;
            })
            .catch(handleError);
        }


        // =========================================================
        // REPORTS
        // =========================================================

        function getPatientReport(patientId) {

            return request(
                "GET",
                API_ROOT + "/reports/patient/" + patientId
            );
        }


        // =========================================================
        // DASHBOARD
        // =========================================================

        function getDashboard() {

            return request(
                "GET",
                API_URL + "/dashboard"
            );
        }


        // =========================================================
        // SPECIALISTS
        // =========================================================

        function getSpecialists(params) {

            return request(
                "GET",
                API_ROOT + "/specialists/available",
                null,
                {
                    params: params || {}
                }
            );
        }

        function submitSpecialistOpinion(payload) {

            return request(
                "POST",
                API_ROOT + "/specialists/opinion",
                payload
            );
        }


        // =========================================================
        // WORKFLOW
        // =========================================================

        function getWorkflow(patientId) {

            return request(
                "GET",
                API_ROOT + "/workflow/patient/" + patientId
            );
        }

        function updateWorkflow(patientId, payload) {

            return request(
                "POST",
                API_ROOT + "/workflow/update/" + patientId,
                payload
            );
        }

        function getWorkflowProgress(patientId) {

            return request(
                "GET",
                API_ROOT + "/workflow/progress/" + patientId
            );
        }

        function getWorkflowHistory(patientId) {

            return request(
                "GET",
                API_ROOT + "/workflow/history/" + patientId
            );
        }

        function getWorkflowStatuses() {

            return request(
                "GET",
                API_ROOT + "/workflow/statuses"
            );
        }


        // =========================================================
        // AUDIT
        // =========================================================

        function getAuditLogs(params) {

            return request(
                "GET",
                API_URL + "/audit/",
                null,
                {
                    params: params || {}
                }
            );
        }

        function getMyAuditLogs(params) {

            return request(
                "GET",
                API_URL + "/audit/user/me",
                null,
                {
                    params: params || {}
                }
            );
        }

        function createAuditLog(payload) {

            return request(
                "POST",
                API_URL + "/audit/log",
                payload
            );
        }

    }

})();