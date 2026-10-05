(function () {
    "use strict";

    angular
        .module("MultiModalCancerTherapy")
        .controller("AuditController", AuditController);

    AuditController.$inject = [
        "$scope",
        "ApiService",
        "AuthService"
    ];

    function AuditController(
        $scope,
        ApiService,
        AuthService
    ) {

        // =========================================================
        // INITIAL STATE
        // =========================================================

        $scope.loading = false;
        $scope.errorMessage = "";
        $scope.successMessage = "";

        $scope.currentUser =
            AuthService.getCurrentUser();

        $scope.auditLogs = [];

        $scope.searchText = "";

        $scope.filterEntityType = "";
        $scope.filterAction = "";

        $scope.selectedLog = null;

        $scope.stats = {
            total: 0,
            today: 0,
            userEvents: 0
        };


        // =========================================================
        // LOAD AUDIT LOGS
        // =========================================================

        $scope.loadAuditLogs = function () {

            $scope.loading = true;
            $scope.errorMessage = "";

            var params = {};

            if ($scope.filterEntityType) {
                params.entity_type =
                    $scope.filterEntityType;
            }

            if ($scope.filterAction) {
                params.action =
                    $scope.filterAction;
            }

            ApiService.getAuditLogs(params)
                .then(function (data) {

                    processAuditData(data);

                })
                .catch(function (error) {

                    console.error(
                        "Audit log loading error:",
                        error
                    );

                    $scope.errorMessage =
                        error && error.message
                            ? error.message
                            : "Unable to load audit records.";

                    $scope.auditLogs = [];
                    updateStats();
                })
                .finally(function () {

                    $scope.loading = false;
                });
        };


        // =========================================================
        // PROCESS DATA
        // =========================================================

        function processAuditData(data) {

            if (Array.isArray(data)) {

                $scope.auditLogs = data;

            } else if (
                data &&
                Array.isArray(data.items)
            ) {

                $scope.auditLogs =
                    data.items;

            } else if (
                data &&
                Array.isArray(data.logs)
            ) {

                $scope.auditLogs =
                    data.logs;

            } else {

                $scope.auditLogs = [];
            }

            updateStats();
        }


        // =========================================================
        // STATISTICS
        // =========================================================

        function updateStats() {

            $scope.stats.total =
                $scope.auditLogs.length;

            $scope.stats.today =
                $scope.auditLogs.filter(
                    isToday
                ).length;

            $scope.stats.userEvents =
                $scope.auditLogs.filter(
                    belongsToCurrentUser
                ).length;
        }


        function isToday(log) {

            if (!log || !log.created_at) {
                return false;
            }

            var date =
                new Date(log.created_at);

            var now =
                new Date();

            return (
                date.getFullYear() ===
                    now.getFullYear() &&

                date.getMonth() ===
                    now.getMonth() &&

                date.getDate() ===
                    now.getDate()
            );
        }


        function belongsToCurrentUser(log) {

            if (
                !$scope.currentUser ||
                !log
            ) {
                return false;
            }

            return String(
                log.user_id || ""
            ) === String(
                $scope.currentUser.id || ""
            );
        }


        // =========================================================
        // SEARCH / FILTER
        // =========================================================

        $scope.filteredAuditLogs = function () {

            var query =
                String(
                    $scope.searchText || ""
                )
                .trim()
                .toLowerCase();

            if (!query) {
                return $scope.auditLogs;
            }

            return $scope.auditLogs.filter(
                function (log) {

                    var values = [
                        log.action,
                        log.entity_type,
                        log.entity_id,
                        log.description,
                        log.ip_address,
                        log.user_id,
                        log.created_at
                    ];

                    return values.some(
                        function (value) {

                            return String(
                                value || ""
                            )
                            .toLowerCase()
                            .indexOf(query) !== -1;

                        }
                    );
                }
            );
        };


        // =========================================================
        // ACTION FILTER
        // =========================================================

        $scope.getActions = function () {

            var unique = {};

            $scope.auditLogs.forEach(
                function (log) {

                    if (log && log.action) {

                        unique[
                            String(log.action)
                        ] = true;
                    }
                }
            );

            return Object.keys(unique).sort();
        };


        // =========================================================
        // ENTITY FILTER
        // =========================================================

        $scope.getEntityTypes = function () {

            var unique = {};

            $scope.auditLogs.forEach(
                function (log) {

                    if (
                        log &&
                        log.entity_type
                    ) {

                        unique[
                            String(log.entity_type)
                        ] = true;
                    }
                }
            );

            return Object.keys(unique).sort();
        };


        // =========================================================
        // FILTER CHANGE
        // =========================================================

        $scope.applyFilters = function () {

            $scope.loadAuditLogs();
        };


        // =========================================================
        // CLEAR FILTERS
        // =========================================================

        $scope.clearFilters = function () {

            $scope.searchText = "";
            $scope.filterEntityType = "";
            $scope.filterAction = "";

            $scope.loadAuditLogs();
        };


        // =========================================================
        // VIEW LOG
        // =========================================================

        $scope.viewLog = function (log) {

            if (!log) {
                return;
            }

            $scope.selectedLog = log;
        };


        // =========================================================
        // CLOSE LOG
        // =========================================================

        $scope.closeLog = function () {

            $scope.selectedLog = null;
        };


        // =========================================================
        // LOG ICON
        // =========================================================

        $scope.getActionIcon = function (action) {

            var value =
                String(action || "")
                    .toLowerCase();

            if (
                value.indexOf("login") !== -1
            ) {
                return "bi-box-arrow-in-right";
            }

            if (
                value.indexOf("logout") !== -1
            ) {
                return "bi-box-arrow-right";
            }

            if (
                value.indexOf("create") !== -1 ||
                value.indexOf("register") !== -1
            ) {
                return "bi-plus-circle";
            }

            if (
                value.indexOf("update") !== -1 ||
                value.indexOf("edit") !== -1
            ) {
                return "bi-pencil";
            }

            if (
                value.indexOf("delete") !== -1
            ) {
                return "bi-trash";
            }

            if (
                value.indexOf("ai") !== -1 ||
                value.indexOf("analysis") !== -1
            ) {
                return "bi-cpu";
            }

            if (
                value.indexOf("workflow") !== -1
            ) {
                return "bi-diagram-3";
            }

            if (
                value.indexOf("report") !== -1
            ) {
                return "bi-file-earmark-text";
            }

            return "bi-clock-history";
        };


        // =========================================================
        // BADGE CLASS
        // =========================================================

        $scope.getActionClass = function (action) {

            var value =
                String(action || "")
                    .toLowerCase();

            if (
                value.indexOf("delete") !== -1 ||
                value.indexOf("fail") !== -1 ||
                value.indexOf("reject") !== -1
            ) {
                return "mmct-badge-danger";
            }

            if (
                value.indexOf("login") !== -1 ||
                value.indexOf("create") !== -1 ||
                value.indexOf("register") !== -1
            ) {
                return "mmct-badge-success";
            }

            if (
                value.indexOf("update") !== -1 ||
                value.indexOf("edit") !== -1
            ) {
                return "mmct-badge-primary";
            }

            if (
                value.indexOf("review") !== -1 ||
                value.indexOf("pending") !== -1
            ) {
                return "mmct-badge-warning";
            }

            return "mmct-badge-secondary";
        };


        // =========================================================
        // FORMAT DATE
        // =========================================================

        $scope.formatDate = function (value) {

            if (!value) {
                return "N/A";
            }

            var date =
                new Date(value);

            if (isNaN(date.getTime())) {
                return String(value);
            }

            return date.toLocaleString();
        };


        // =========================================================
        // REFRESH
        // =========================================================

        $scope.refreshAudit = function () {

            $scope.successMessage = "";

            $scope.loadAuditLogs();
        };


        // =========================================================
        // INITIAL LOAD
        // =========================================================

        $scope.loadAuditLogs();
    }

})();