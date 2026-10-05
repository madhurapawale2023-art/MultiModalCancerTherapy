(function () {
    "use strict";

    angular
        .module("MultiModalCancerTherapy")
        .controller("LoginController", LoginController);

    LoginController.$inject = ["$scope", "$location", "ApiService", "AuthService"];

    function LoginController($scope, $location, ApiService, AuthService) {

        // =========================================================
        // Initial State
        // =========================================================

        $scope.loginData = {
            username: "",
            password: ""
        };

        $scope.loading = false;
        $scope.isLoading = false;
        $scope.loginSubmitted = false;
        $scope.errorMessage = "";
        $scope.successMessage = "";
        $scope.showPassword = false;

        // =========================================================
        // Clear Messages
        // =========================================================

        $scope.clearMessages = function () {

            $scope.errorMessage = "";
            $scope.successMessage = "";
        };

        // =========================================================
        // Login
        // =========================================================

        $scope.login = function (loginForm) {

            $scope.loginSubmitted = true;

            $scope.errorMessage = "";
            $scope.successMessage = "";

            var username = ($scope.loginData.username || "").trim();
            var password = $scope.loginData.password || "";

            if (!username) {
                $scope.errorMessage = "Please enter your username.";
                return;
            }

            if (!password) {
                $scope.errorMessage = "Please enter your password.";
                return;
            }

            $scope.loading = true;
            $scope.isLoading = true;

            ApiService.login({
                username: username,
                password: password
            })
            .then(function (data) {

                if (!data || !data.access_token) {
                    throw new Error("Authentication token was not returned by the server.");
                }

                // Store access token
                localStorage.setItem(
                    "mmct_access_token",
                    data.access_token
                );

                // Store user data when returned by backend
                if (data.user) {
                    localStorage.setItem(
                        "mmct_current_user",
                        JSON.stringify(data.user)
                    );
                }

                // Also let AuthService manage session
                if (typeof AuthService.setSession === "function") {
                    AuthService.setSession(data);
                }

                $scope.successMessage = "Login successful. Redirecting...";

                // Redirect to dashboard
                $location.path("/dashboard");
            })
            .catch(function (error) {

                console.error("Login Error:", error);

                if (error && error.message) {
                    $scope.errorMessage = error.message;
                } else if (error && error.data && error.data.detail) {
                    $scope.errorMessage = error.data.detail;
                } else {
                    $scope.errorMessage =
                        "Login failed. Please check your username and password.";
                }
            })
            .finally(function () {
                $scope.loading = false;
                $scope.isLoading = false;
            });
        };

        // =========================================================
        // Toggle Password Visibility
        // =========================================================

        $scope.togglePassword = function () {
            $scope.showPassword = !$scope.showPassword;
        };

        // =========================================================
        // Demo Admin Login
        // =========================================================

        $scope.useDemoAdmin = function () {
            $scope.loginData.username = "admin";
            $scope.loginData.password = "Admin@123";

            $scope.clearMessages();
        };

        // =========================================================
        // Demo Senior Doctor Login
        // =========================================================

        $scope.useDemoDoctor = function () {
            $scope.loginData.username = "senior.doctor";
            $scope.loginData.password = "Doctor@123";

            $scope.clearMessages();
        };

        // =========================================================
        // Keyboard Support
        // =========================================================

        $scope.handleKeyPress = function (event) {

            if (event && event.which === 13) {
                $scope.login();
            }
        };

        // =========================================================
        // Initialization
        // =========================================================

        $scope.init = function () {
            $scope.loading = false;
            $scope.isLoading = false;
            $scope.loginSubmitted = false;
            $scope.errorMessage = "";
            $scope.successMessage = "";
        };

        $scope.init();
    }

})();