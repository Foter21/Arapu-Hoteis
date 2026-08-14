/* =====================================================
   ARAPUÁ HOTÉIS
   JAVASCRIPT DO DASHBOARD
   ===================================================== */

document.addEventListener("DOMContentLoaded", function () {

    /* =====================================================
       MENU MOBILE
    ===================================================== */

    const mobileMenu = document.getElementById("mobileMenu");
    const sidebar = document.getElementById("sidebar");

    if (mobileMenu && sidebar) {

        mobileMenu.addEventListener("click", function () {

            sidebar.classList.toggle("open");

        });

    }


    /* =====================================================
       MENU LATERAL
    ===================================================== */

    const menuItems = document.querySelectorAll(".menu-item");

    menuItems.forEach(function (item) {

        item.addEventListener("click", function (event) {

            event.preventDefault();

            menuItems.forEach(function (menu) {
                menu.classList.remove("active");
            });

            item.classList.add("active");

            // Fecha o menu no celular
            if (window.innerWidth <= 1199) {
                sidebar.classList.remove("open");
            }

        });

    });


    /* =====================================================
       SELETOR DE PERÍODO
    ===================================================== */

    const periodSelect = document.getElementById("periodSelect");

    if (periodSelect) {

        periodSelect.addEventListener("change", function () {

            console.log(
                "Período selecionado:",
                this.value
            );

            /*
                Aqui futuramente você pode conectar
                o seletor ao banco de dados.
            */

        });

    }


    /* =====================================================
       NOTIFICAÇÕES
    ===================================================== */

    const notificationButton =
        document.getElementById("notificationButton");

    if (notificationButton) {

        notificationButton.addEventListener("click", function () {

            alert(
                "Você possui 3 notificações pendentes."
            );

        });

    }


    /* =====================================================
       RESERVAS
    ===================================================== */

    const reservations =
        document.querySelectorAll(".reservation");

    reservations.forEach(function (reservation) {

        reservation.addEventListener("click", function () {

            const guest =
                reservation.querySelector(
                    ".reservation-info strong"
                );

            if (guest) {

                alert(
                    "Reserva de " +
                    guest.textContent.trim()
                );

            }

        });

    });


    /* =====================================================
       VER TODAS AS RESERVAS
    ===================================================== */

    const viewReservations =
        document.getElementById("viewReservations");

    if (viewReservations) {

        viewReservations.addEventListener(
            "click",
            function () {

                alert(
                    "Abrindo todas as reservas..."
                );

            }
        );

    }


    /* =====================================================
       ALERTAS
    ===================================================== */

    const alerts =
        document.querySelectorAll(".alert-item");

    alerts.forEach(function (alertItem) {

        alertItem.addEventListener(
            "click",
            function () {

                const title =
                    alertItem.querySelector(
                        "strong"
                    );

                if (title) {

                    alert(
                        title.textContent.trim()
                    );

                }

            }
        );

    });


    /* =====================================================
       BOTÃO SAIR
    ===================================================== */

    const logoutButton =
        document.getElementById("logoutButton");

    if (logoutButton) {

        logoutButton.addEventListener(
            "click",
            function () {

                const confirmar =
                    confirm(
                        "Deseja realmente sair do sistema?"
                    );

                if (confirmar) {

                    /*
                       Se estiver usando Flask,
                       você pode trocar por:

                       window.location.href =
                       "/logout";
                    */

                    console.log(
                        "Usuário saiu do sistema."
                    );

                }

            }
        );

    }


    /* =====================================================
       ANIMAÇÃO DOS NÚMEROS
    ===================================================== */

    const numbers =
        document.querySelectorAll(
            ".stat-info strong"
        );

    numbers.forEach(function (number) {

        number.style.opacity = "0";

        setTimeout(function () {

            number.style.transition =
                "opacity .5s ease";

            number.style.opacity = "1";

        }, 150);

    });


    /* =====================================================
       ANIMAÇÃO DAS BARRAS
    ===================================================== */

    const bars =
        document.querySelectorAll(".bar");

    bars.forEach(function (bar) {

        const height =
            bar.style.height;

        bar.style.height = "0";

        setTimeout(function () {

            bar.style.height = height;

        }, 300);

    });

});
