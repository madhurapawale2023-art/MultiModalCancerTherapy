(function () {
    "use strict";

    angular
        .module("MultiModalCancerTherapy")

        // =========================================================
        // APPLICATION CONFIGURATION
        // =========================================================

        .constant("APP_CONFIG", {
            appName: "MultiModalCancerTherapy",

            apiBaseUrl: "http://127.0.0.1:8000",
            apiPrefix: "/api",

            version: "1.0.0",

            frontend: {
                framework: "AngularJS",
                version: "1.8.3",
                ui: "Bootstrap 5",
                charts: "Chart.js"
            },

            backend: {
                framework: "FastAPI",
                database: "PostgreSQL 17"
            },

            clinicalDecisionSupportOnly: true,
            seniorDoctorFinalAuthority: true,

            // =====================================================
            // DNA MODULE IS DISABLED
            // =====================================================

            dnaTestingEnabled: false
        })

        // =========================================================
        // APPLICATION RUN BLOCK
        // =========================================================

        .run(AppRun);

    AppRun.$inject = [
        "$rootScope",
        "$location",
        "$route",
        "APP_CONFIG",
        "AuthService"
    ];

    function AppRun(
        $rootScope,
        $location,
        $route,
        APP_CONFIG,
        AuthService
    ) {

        // =========================================================
        // GLOBAL APPLICATION STATE
        // =========================================================

        $rootScope.appConfig = APP_CONFIG;

        $rootScope.currentUser = AuthService.getCurrentUser();

        $rootScope.isAuthenticated = AuthService.isAuthenticated();

        // =========================================================
        // AUTH STATE UPDATE
        // =========================================================

        function updateAuthState() {

            $rootScope.currentUser =
                AuthService.getCurrentUser();

            $rootScope.isAuthenticated =
                AuthService.isAuthenticated();
        }

        // =========================================================
        // ROUTE PROTECTION
        // =========================================================

        $rootScope.$on(
            "$routeChangeStart",
            function (event, next) {

                if (!next) {
                    return;
                }

                var requiresAuth =
                    next.requiresAuth === true;

                var authenticated =
                    AuthService.isAuthenticated();

                // -------------------------------------------------
                // Protected route without login
                // -------------------------------------------------

                if (requiresAuth && !authenticated) {

                    event.preventDefault();

                    updateAuthState();

                    $location.path("/login");

                    return;
                }

                // -------------------------------------------------
                // Already logged in -> don't show login page
                // -------------------------------------------------

                if (
                    next.templateUrl === "views/login.html" &&
                    authenticated
                ) {

                    event.preventDefault();

                    updateAuthState();

                    $location.path("/dashboard");

                    return;
                }

                updateAuthState();
            }
        );

        // =========================================================
        // ROUTE SUCCESS
        // =========================================================

        $rootScope.$on(
            "$routeChangeSuccess",
            function () {

                updateAuthState();

                $rootScope.pageLoading = false;
            }
        );

        // =========================================================
        // ROUTE ERROR
        // =========================================================

        $rootScope.$on(
            "$routeChangeError",
            function () {

                $rootScope.pageLoading = false;

                if (!AuthService.isAuthenticated()) {
                    $location.path("/login");
                }
            }
        );

        // =========================================================
        // REQUEST / PAGE LOADING STATE
        // =========================================================

        $rootScope.pageLoading = false;

        // =========================================================
        // APPLICATION INITIALIZATION
        // =========================================================

        AuthService.initialize()
            .then(function (user) {

                $rootScope.currentUser = user;

                $rootScope.isAuthenticated =
                    AuthService.isAuthenticated();

            })
            .catch(function () {

                $rootScope.currentUser = null;

                $rootScope.isAuthenticated = false;
            });

        // =========================================================
        // GLOBAL LOGOUT EVENT
        // =========================================================

        $rootScope.$on(
            "mmct:logout",
            function () {

                AuthService.clearSession();

                updateAuthState();

                $location.path("/login");
            }
        );

        // =========================================================
        // GLOBAL LOGIN EVENT
        // =========================================================

        $rootScope.$on(
            "mmct:login",
            function () {

                updateAuthState();
            }
        );
    }

})();