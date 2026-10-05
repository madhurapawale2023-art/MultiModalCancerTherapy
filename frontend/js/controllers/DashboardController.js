(function () {
    "use strict";

    angular
        .module("MultiModalCancerTherapy")
        .controller("DashboardController", DashboardController);

    DashboardController.$inject = [
        "$scope",
        "$location",
        "$q",
        "$timeout",
        "ApiService",
        "AuthService"
    ];

    function DashboardController(
        $scope,
        $location,
        $q,
        $timeout,
        ApiService,
        AuthService
    ) {

        // =========================================================
        // INITIAL STATE
        // =========================================================

        $scope.loading = true;
        $scope.errorMessage = "";

        $scope.currentUser = AuthService.getCurrentUser();

        $scope.stats = {
            totalPatients: 0,
            activeCases: 0,
            aiAnalyses: 0,
            pendingReviews: 0
        };

        $scope.recentPatients = [];

        $scope.systemHealth = {
            backend: false,
            database: false,
            overall: false
        };

        $scope.aiStatus = {
            status: "checking",
            clinicalModel: false,
            clinicalPreprocessor: false,
            targetEncoder: false,
            ultrasoundModel: false,
            ultrasoundModelInfo: false,
            clinicalDecisionSupportOnly: true,
            seniorDoctorReviewRequired: true
        };

        // Aggregated real project data (from /api/dashboard)
        $scope.dashboardData = null;

        // Training CSV summary (real values, read-only)
        $scope.trainingInfo = {
            available: false,
            fileName: "",
            relativePath: "",
            rows: null,
            columns: null,
            targetClasses: null,
            ageStatistics: null
        };

        // Trained-model metrics (real values from model metadata)
        $scope.modelMetrics = {
            clinical: null,
            ultrasound: null,
            multimodal: null
        };

        // Clinical training metadata (feature_info.json)
        $scope.clinicalTraining = null;

        // Chart data built from real project data only
        $scope.chartData = {
            diagnosisLabels: [],
            diagnosisValues: [],
            modelLabels: [],
            modelValues: []
        };

        $scope.workflowSteps = [
            {
                step: 1,
                title: "Patient Registration",
                status: "Pending"
            },
            {
                step: 2,
                title: "Clinical Data",
                status: "Pending"
            },
            {
                step: 3,
                title: "Laboratory Review",
                status: "Pending"
            },
            {
                step: 4,
                title: "Pathology Review",
                status: "Pending"
            },
            {
                step: 5,
                title: "Ultrasound / Imaging",
                status: "Pending"
            },
            {
                step: 6,
                title: "AI Clinical Analysis",
                status: "Pending"
            },
            {
                step: 7,
                title: "Multimodal Evidence",
                status: "Pending"
            },
            {
                step: 8,
                title: "Specialist Review",
                status: "Pending"
            },
            {
                step: 9,
                title: "Treatment Planning",
                status: "Pending"
            },
            {
                step: 10,
                title: "Senior Doctor Review",
                status: "Pending"
            },
            {
                step: 11,
                title: "Final Decision",
                status: "Pending"
            }
        ];


        // =========================================================
        // LOAD DASHBOARD
        // =========================================================

        $scope.loadDashboard = function () {

            $scope.loading = true;
            $scope.errorMessage = "";

            var currentUserPromise = loadCurrentUser();
            var healthPromise = loadHealth();
            var aiPromise = loadAIStatus();
            var patientsPromise = loadPatients();
            var dashboardPromise = loadDashboardData();

            $q.all({
                user: currentUserPromise,
                health: healthPromise,
                ai: aiPromise,
                patients: patientsPromise,
                dashboard: dashboardPromise
            })
            .then(function (result) {

                if (result.user) {
                    $scope.currentUser = result.user;
                }

                if (result.health) {
                    processHealth(result.health);
                }

                if (result.ai) {
                    processAIStatus(result.ai);
                }

                if (result.patients) {
                    processPatients(result.patients);
                }

                if (result.dashboard) {
                    processDashboard(result.dashboard);
                }

            })
            .catch(function (error) {

                console.error(
                    "Dashboard loading error:",
                    error
                );

                $scope.errorMessage =
                    error && error.message
                        ? error.message
                        : "Unable to load dashboard data.";

            })
            .finally(function () {

                $scope.loading = false;
            });
        };


        // =========================================================
        // CURRENT USER
        // =========================================================

        function loadCurrentUser() {

            if (!AuthService.isAuthenticated()) {
                return $q.when(null);
            }

            return ApiService.getCurrentUser()
                .then(function (user) {

                    if (user) {
                        $scope.currentUser = user;
                    }

                    return user;
                })
                .catch(function (error) {

                    console.warn(
                        "Current user could not be loaded:",
                        error
                    );

                    return $scope.currentUser;
                });
        }


        // =========================================================
        // HEALTH
        // =========================================================

        function loadHealth() {

            return ApiService.health()
                .then(function (data) {
                    return data;
                })
                .catch(function (error) {

                    console.warn(
                        "Health API error:",
                        error
                    );

                    return null;
                });
        }

        function processHealth(data) {

            if (!data) {
                return;
            }

            $scope.systemHealth.backend = true;

            /*
             * /health returns:
             *   "database": "PostgreSQL" | "Unavailable"
             *   "database_connection": true | false
             * Older/alternate keys are also accepted.
             */
            if (
                data.database_connection === true ||
                data.database === true ||
                data.postgresql === true ||
                data.db === true
            ) {
                $scope.systemHealth.database = true;
            }

            /*
             * When /health returns successfully we consider the
             * backend healthy. Database flag is shown separately.
             */
            $scope.systemHealth.overall = true;
        }


        // =========================================================
        // AI STATUS
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

        function processAIStatus(data) {

            if (!data) {
                return;
            }

            $scope.aiStatus = angular.extend(
                $scope.aiStatus,
                data
            );

            if (data.status) {
                $scope.aiStatus.status =
                    String(data.status).toLowerCase();
            }
        }


        // =========================================================
        // PATIENTS
        // =========================================================

        function loadPatients() {

            return ApiService.getPatients({
                page: 1,
                page_size: 10
            })
            .then(function (data) {
                return data;
            })
            .catch(function (error) {

                console.warn(
                    "Patient API error:",
                    error
                );

                /*
                 * Dashboard should still load even when the
                 * patient table is empty.
                 */
                return {
                    items: [],
                    total: 0
                };
            });
        }

        function processPatients(data) {

            var items = [];

            if (Array.isArray(data)) {
                items = data;
            }
            else if (data && Array.isArray(data.items)) {
                items = data.items;
            }

            $scope.recentPatients = items.slice(0, 10);

            var total = 0;

            if (data && angular.isNumber(data.total)) {
                total = data.total;
            }
            else {
                total = items.length;
            }

            $scope.stats.totalPatients = total;

            /*
             * Active cases are calculated only from available
             * patient workflow/status information.
             */
            $scope.stats.activeCases = items.filter(function (patient) {

                var status = String(
                    patient.workflow_status ||
                    patient.status ||
                    ""
                ).toLowerCase();

                return status &&
                    status !== "completed" &&
                    status !== "closed";
            }).length;
        }


        // =========================================================
        // DASHBOARD DATA (/api/dashboard)
        // =========================================================

        function loadDashboardData() {

            return ApiService.getDashboard()
                .catch(function (error) {

                    console.warn(
                        "Dashboard API error:",
                        error
                    );

                    return null;
                });
        }

        function processDashboard(data) {

            if (!data) {
                return;
            }

            $scope.dashboardData = data;

            if (data.patients) {

                if (angular.isNumber(data.patients.total)) {
                    $scope.stats.totalPatients =
                        data.patients.total;
                }

                if (angular.isNumber(data.patients.active)) {
                    $scope.stats.activeCases =
                        data.patients.active;
                }
            }

            if (data.records) {

                if (angular.isNumber(data.records.ai_analyses)) {
                    $scope.stats.aiAnalyses =
                        data.records.ai_analyses;
                }

                if (angular.isNumber(data.records.pending_reviews)) {
                    $scope.stats.pendingReviews =
                        data.records.pending_reviews;
                }
            }

            if (data.dataset && data.dataset.available) {

                $scope.trainingInfo = {
                    available: true,
                    fileName: data.dataset.file_name || "",
                    relativePath: data.dataset.relative_path || "",
                    rows: data.dataset.rows,
                    columns: data.dataset.columns,
                    targetClasses: data.dataset.target_classes,
                    ageStatistics: data.dataset.age_statistics || null
                };
            }

            if (data.clinical_model) {

                $scope.modelMetrics.clinical =
                    data.clinical_model.metrics || null;

                $scope.clinicalTraining =
                    data.clinical_model.feature_info || null;
            }

            if (data.ultrasound_model) {
                $scope.modelMetrics.ultrasound =
                    data.ultrasound_model;
            }

            if (data.multimodal) {
                $scope.modelMetrics.multimodal =
                    data.multimodal.summary || null;
            }

            buildChartData(data);

            $timeout(renderCharts, 0);
        }

        function buildChartData(data) {

            var dataset = data && data.dataset;

            if (!dataset || !dataset.available) {
                return;
            }

            var distribution = dataset.target_distribution || {};

            var entries = Object.keys(distribution).map(
                function (key) {
                    return {
                        label: key,
                        value: distribution[key]
                    };
                }
            );

            entries.sort(function (first, second) {
                return second.value - first.value;
            });

            var top = entries.slice(0, 10);

            $scope.chartData.diagnosisLabels = top.map(
                function (item) {
                    return item.label;
                }
            );

            $scope.chartData.diagnosisValues = top.map(
                function (item) {
                    return item.value;
                }
            );
        }


        // =========================================================
        // CHART.JS RENDERING (real data only)
        // =========================================================

        function renderCharts() {

            if (typeof window.Chart === "undefined") {
                return;
            }

            renderDiagnosisChart();

            renderModelChart();
        }

        function renderDiagnosisChart() {

            var canvas = document.getElementById(
                "mmctDiagnosisChart"
            );

            if (!canvas || !$scope.chartData.diagnosisLabels.length) {
                return;
            }

            if (canvas.__mmctChart) {
                canvas.__mmctChart.destroy();
            }

            canvas.__mmctChart = new window.Chart(canvas, {
                type: "bar",
                data: {
                    labels: $scope.chartData.diagnosisLabels,
                    datasets: [{
                        label: "Training diagnoses",
                        data: $scope.chartData.diagnosisValues,
                        backgroundColor: "rgba(13,110,253,0.65)",
                        borderRadius: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        y: { beginAtZero: true }
                    }
                }
            });
        }

        function renderModelChart() {

            var canvas = document.getElementById(
                "mmctModelChart"
            );

            if (!canvas) {
                return;
            }

            var labels = [];
            var values = [];

            var clinical = $scope.modelMetrics.clinical;

            if (clinical && angular.isNumber(clinical.accuracy)) {
                labels.push("Clinical accuracy");
                values.push(
                    Math.round(clinical.accuracy * 1000) / 10
                );
            }

            if (clinical && angular.isNumber(clinical.weighted_f1)) {
                labels.push("Clinical F1");
                values.push(
                    Math.round(clinical.weighted_f1 * 1000) / 10
                );
            }

            var ultrasound = $scope.modelMetrics.ultrasound;

            if (ultrasound && angular.isNumber(ultrasound.test_dice)) {
                labels.push("Ultrasound Dice");
                values.push(
                    Math.round(ultrasound.test_dice * 1000) / 10
                );
            }

            if (ultrasound && angular.isNumber(ultrasound.test_iou)) {
                labels.push("Ultrasound IoU");
                values.push(
                    Math.round(ultrasound.test_iou * 1000) / 10
                );
            }

            if (!labels.length) {
                return;
            }

            if (canvas.__mmctChart) {
                canvas.__mmctChart.destroy();
            }

            canvas.__mmctChart = new window.Chart(canvas, {
                type: "bar",
                data: {
                    labels: labels,
                    datasets: [{
                        label: "Model performance (%)",
                        data: values,
                        backgroundColor: "rgba(25,135,84,0.65)",
                        borderRadius: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        y: { beginAtZero: true, max: 100 }
                    }
                }
            });
        }


        // =========================================================
        // PATIENT NAVIGATION
        // =========================================================

        $scope.openPatient = function (patient) {

            if (!patient || !patient.id) {
                return;
            }

            $location.path(
                "/patients/" + patient.id
            );
        };


        $scope.viewAllPatients = function () {
            $location.path("/patients");
        };


        // =========================================================
        // QUICK ACTIONS
        // =========================================================

        $scope.goToPatients = function () {
            $location.path("/patients");
        };


        $scope.registerPatient = function () {
            $location.path("/patients");
        };


        $scope.goToAIAnalysis = function () {
            $location.path("/ai-analysis");
        };


        $scope.goToReports = function () {
            $location.path("/reports");
        };


        $scope.goToSpecialists = function () {
            $location.path("/specialists");
        };


        $scope.goToWorkflow = function () {
            $location.path("/workflow");
        };


        $scope.goToAudit = function () {
            $location.path("/audit");
        };


        // =========================================================
        // REFRESH
        // =========================================================

        $scope.refreshDashboard = function () {
            $scope.loadDashboard();
        };


        // =========================================================
        // LOGOUT
        // =========================================================

        $scope.logout = function () {

            AuthService.logout();
        };


        // =========================================================
        // ROLE HELPERS FOR UI
        // =========================================================

        $scope.isAdmin = function () {
            return AuthService.isAdmin();
        };

        $scope.isSeniorDoctor = function () {
            return AuthService.isSeniorDoctor();
        };

        $scope.isAssistantDoctor = function () {
            return AuthService.isAssistantDoctor();
        };

        $scope.isPathologist = function () {
            return AuthService.isPathologist();
        };

        $scope.isRadiologist = function () {
            return AuthService.isRadiologist();
        };

        $scope.isLabStaff = function () {
            return AuthService.isLabStaff();
        };


        // =========================================================
        // USER DISPLAY
        // =========================================================

        $scope.getUserName = function () {

            var user = $scope.currentUser;

            if (!user) {
                return "Clinical User";
            }

            return (
                user.full_name ||
                user.username ||
                "Clinical User"
            );
        };


        $scope.getUserRole = function () {

            var user = $scope.currentUser;

            if (!user) {
                return "";
            }

            return (
                user.role ||
                user.role_name ||
                ""
            );
        };


        // =========================================================
        // AI READINESS
        // =========================================================

        $scope.isAIReady = function () {

            return (
                $scope.aiStatus.status === "ready" ||
                $scope.aiStatus.status === "active"
            );
        };


        // =========================================================
        // INITIALIZE
        // =========================================================

        $scope.loadDashboard();
    }

})();