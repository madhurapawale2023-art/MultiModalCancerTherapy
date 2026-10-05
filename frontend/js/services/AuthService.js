(function () {
    "use strict";

    angular
        .module("MultiModalCancerTherapy")
        .factory("AuthService", AuthService);

    AuthService.$inject = ["$q", "$location", "ApiService"];

    function AuthService($q, $location, ApiService) {

        var TOKEN_KEY = "mmct_access_token";
        var USER_KEY = "mmct_current_user";

        var currentUser = null;
        var initialized = false;

        var service = {
            login: login,
            logout: logout,
            isAuthenticated: isAuthenticated,
            getToken: getToken,
            getCurrentUser: getCurrentUser,
            setSession: setSession,
            clearSession: clearSession,
            loadCurrentUser: loadCurrentUser,
            initialize: initialize,
            hasRole: hasRole,
            hasAnyRole: hasAnyRole,
            isAdmin: isAdmin,
            isSeniorDoctor: isSeniorDoctor,
            isAssistantDoctor: isAssistantDoctor,
            isPathologist: isPathologist,
            isRadiologist: isRadiologist,
            isLabStaff: isLabStaff,
            getAuthHeader: getAuthHeader
        };

        return service;

        // =========================================================
        // LOGIN
        // =========================================================

        function login(username, password) {

            return ApiService.login({
                username: username,
                password: password
            })
            .then(function (data) {

                if (!data || !data.access_token) {
                    return $q.reject({
                        message: "Authentication token was not returned."
                    });
                }

                setSession(data);

                return data;
            });
        }

        // =========================================================
        // SET SESSION
        // =========================================================

        function setSession(data) {

            if (!data) {
                return;
            }

            if (data.access_token) {
                localStorage.setItem(
                    TOKEN_KEY,
                    data.access_token
                );
            }

            if (data.user) {

                currentUser = data.user;

                localStorage.setItem(
                    USER_KEY,
                    JSON.stringify(data.user)
                );
            }

            initialized = true;
        }

        // =========================================================
        // LOAD CURRENT USER
        // =========================================================

        function loadCurrentUser() {

            var token = getToken();

            if (!token) {
                currentUser = null;
                initialized = true;

                return $q.reject({
                    message: "User is not authenticated."
                });
            }

            return ApiService.getCurrentUser()
                .then(function (user) {

                    currentUser = user;

                    localStorage.setItem(
                        USER_KEY,
                        JSON.stringify(user)
                    );

                    initialized = true;

                    return user;
                })
                .catch(function (error) {

                    clearSession();

                    return $q.reject(error);
                });
        }

        // =========================================================
        // INITIALIZE SESSION
        // =========================================================

        function initialize() {

            if (initialized) {
                return $q.when(currentUser);
            }

            var token = getToken();

            if (!token) {

                initialized = true;
                currentUser = null;

                return $q.when(null);
            }

            var storedUser = localStorage.getItem(USER_KEY);

            if (storedUser) {

                try {
                    currentUser = JSON.parse(storedUser);
                } catch (e) {
                    currentUser = null;
                }
            }

            return loadCurrentUser()
                .catch(function () {
                    return null;
                });
        }

        // =========================================================
        // LOGOUT
        // =========================================================

        function logout() {

            clearSession();

            $location.path("/login");
        }

        // =========================================================
        // CLEAR SESSION
        // =========================================================

        function clearSession() {

            localStorage.removeItem(TOKEN_KEY);
            localStorage.removeItem(USER_KEY);

            currentUser = null;
            initialized = true;
        }

        // =========================================================
        // AUTH CHECK
        // =========================================================

        function isAuthenticated() {

            var token = getToken();

            return !!token;
        }

        // =========================================================
        // GET TOKEN
        // =========================================================

        function getToken() {

            return localStorage.getItem(TOKEN_KEY);
        }

        // =========================================================
        // GET CURRENT USER
        // =========================================================

        function getCurrentUser() {

            if (currentUser) {
                return currentUser;
            }

            var storedUser = localStorage.getItem(USER_KEY);

            if (!storedUser) {
                return null;
            }

            try {

                currentUser = JSON.parse(storedUser);

                return currentUser;

            } catch (e) {

                return null;
            }
        }

        // =========================================================
        // GET AUTH HEADER
        // =========================================================

        function getAuthHeader() {

            var token = getToken();

            if (!token) {
                return {};
            }

            return {
                Authorization: "Bearer " + token
            };
        }

        // =========================================================
        // ROLE HELPERS
        // =========================================================

        function getRoleName() {

            var user = getCurrentUser();

            if (!user) {
                return "";
            }

            return String(
                user.role ||
                user.role_name ||
                ""
            ).trim().toLowerCase();
        }

        function hasRole(role) {

            if (!role) {
                return false;
            }

            return getRoleName() === String(role).trim().toLowerCase();
        }

        function hasAnyRole(roles) {

            if (!Array.isArray(roles)) {
                return false;
            }

            var roleName = getRoleName();

            return roles.some(function (role) {

                return roleName === String(role)
                    .trim()
                    .toLowerCase();

            });
        }

        // =========================================================
        // SPECIFIC ROLES
        // =========================================================

        function isAdmin() {
            return hasRole("Admin");
        }

        function isSeniorDoctor() {
            return hasRole("Senior Doctor");
        }

        function isAssistantDoctor() {
            return hasRole("Assistant Doctor");
        }

        function isPathologist() {
            return hasRole("Pathologist");
        }

        function isRadiologist() {
            return hasRole("Radiologist");
        }

        function isLabStaff() {
            return hasRole("Lab Staff");
        }
    }

})();