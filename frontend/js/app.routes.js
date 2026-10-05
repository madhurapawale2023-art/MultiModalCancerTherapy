(function () {
    "use strict";

    angular
        .module("MultiModalCancerTherapy")
        .config(AppRoutes);

    AppRoutes.$inject = ["$routeProvider", "$locationProvider"];

    function AppRoutes($routeProvider, $locationProvider) {

        // Use AngularJS hash routing
        $locationProvider.hashPrefix("!");

        $routeProvider

            // =====================================================
            // PUBLIC LOGIN
            // =====================================================

            .when("/login", {
                templateUrl: "views/login.html",
                controller: "LoginController"
            })

            // =====================================================
            // DASHBOARD
            // =====================================================

            .when("/", {
                redirectTo: "/dashboard"
            })

            .when("/dashboard", {
                templateUrl: "views/dashboard.html",
                controller: "DashboardController",
                requiresAuth: true
            })

            // =====================================================
            // PATIENTS
            // =====================================================

            .when("/patients", {
                templateUrl: "views/patients.html",
                controller: "PatientController",
                requiresAuth: true
            })

            .when("/patients/:patientId", {
                templateUrl: "views/patient-detail.html",
                controller: "PatientDetailController",
                requiresAuth: true
            })

            // =====================================================
            // AI ANALYSIS
            // =====================================================

            .when("/ai-analysis", {
                templateUrl: "views/ai-analysis.html",
                controller: "AIController",
                requiresAuth: true
            })

            // =====================================================
            // REPORTS
            // =====================================================

            .when("/reports", {
                templateUrl: "views/reports.html",
                controller: "ReportController",
                requiresAuth: true
            })

            .when("/reports/:patientId", {
                templateUrl: "views/reports.html",
                controller: "ReportController",
                requiresAuth: true
            })

            // =====================================================
            // SPECIALISTS
            // =====================================================

            .when("/specialists", {
                templateUrl: "views/specialists.html",
                controller: "SpecialistController",
                requiresAuth: true
            })

            // =====================================================
            // WORKFLOW
            // =====================================================

            .when("/workflow", {
                templateUrl: "views/workflow.html",
                controller: "WorkflowController",
                requiresAuth: true
            })

            .when("/workflow/:patientId", {
                templateUrl: "views/workflow.html",
                controller: "WorkflowController",
                requiresAuth: true
            })

            // =====================================================
            // AUDIT
            // =====================================================

            .when("/audit", {
                templateUrl: "views/audit.html",
                controller: "AuditController",
                requiresAuth: true
            })

            // =====================================================
            // UNKNOWN ROUTE
            // =====================================================

            .otherwise({
                redirectTo: "/login"
            });
    }

})();