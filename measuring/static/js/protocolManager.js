const protocolManager = {
    currentProtocolId: null,
    drawingId: null,

    async checkAndSelectProtocol(drawingId) {
        this.drawingId = drawingId;

        const result = await django_communicator.checkUnfinishedProtocols(drawingId);
        if (!result || !result.protocols || result.protocols.length === 0) {
            console.log("🟢 No unfinished protocols");
            return null;
        }

        this.showModal(result.protocols);

        return new Promise(resolve => {
            this._resolveSelection = (selectedId) => {
                this.currentProtocolId = selectedId;
                resolve(selectedId);
            };
        });
    },

    showModal(protocols) {
        const modalElement = document.getElementById("unfinished-protocol-modal");
        const container = document.getElementById("unfinished-protocol-options");
        container.innerHTML = "";

        protocols.forEach(protocol => {
            const btn = document.createElement("button");
            btn.className = "btn btn-outline-primary w-100 mb-2";
            btn.textContent = `Continue Protocol #${protocol.id} (${protocol.measured_count} measured)`;

            btn.addEventListener("click", () => {
                this.currentProtocolId = protocol.id;
                this.hideModal();
                if (this._resolveSelection) this._resolveSelection(protocol.id);
            });

            container.appendChild(btn);
        });

    // ✅ Proper way to show Bootstrap modal
    this._modalInstance = new bootstrap.Modal(modalElement);
    this._modalInstance.show();
    },

    hideModal() {
        const modalElement = document.getElementById("unfinished-protocol-modal");
        const modalInstance = bootstrap.Modal.getInstance(modalElement);

        if (modalInstance) {
            modalInstance.hide();

            // ✅ After hiding, move focus to something visible
            setTimeout(() => {
                const fallback = document.getElementById("measurement-input") || document.body;
                fallback.focus();
            }, 300); // wait a moment for Bootstrap to finish hiding
        }
    },

    createNewProtocol() {
        this.currentProtocolId = null;
        console.log("🆕 User chose to create a new protocol");
        this.hideModal();
        if (this._resolveSelection) this._resolveSelection(null);
    }
};

window.protocolManager = protocolManager;
