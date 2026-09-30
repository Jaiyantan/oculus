/**
 * Oculus Fraud Engine SDK
 * 
 * Embed this script into any website to track and analyze transactions in real-time.
 * 
 * Usage in HTML:
 * <script src="http://localhost:3333/oculus-sdk.js"></script>
 * <script>
 *   OculusSDK.init({ apiUrl: 'http://localhost:8000/api/v1' });
 *   
 *   async function onCheckout() {
 *     const result = await OculusSDK.processTransaction({
 *       user_id: "user_test_1",
 *       amount: 150.00,
 *       currency: "USD",
 *       merchant_category: "retail"
 *     });
 *     console.log("Risk Tier:", result.risk_tier);
 *   }
 * </script>
 */

const OculusSDK = (function() {
    let config = {
        apiUrl: 'http://localhost:8000/api/v1'
    };

    // Simple device fingerprinting (mocked for simplicity)
    const getDeviceFingerprint = () => {
        const nav = window.navigator;
        const screen = window.screen;
        const string = nav.userAgent + nav.language + screen.colorDepth + screen.width + screen.height;
        let hash = 0;
        for (let i = 0; i < string.length; i++) {
            const char = string.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash;
        }
        return `fp_${Math.abs(hash)}`;
    };

    return {
        init: function(options) {
            config = { ...config, ...options };
            console.log("🛡️ Oculus Fraud Engine SDK Initialized.");
        },

        processTransaction: async function(transactionData) {
            // Auto-fill missing telemetry data
            const payload = {
                user_id: transactionData.user_id || "anonymous_user",
                amount: transactionData.amount || 0.0,
                currency: transactionData.currency || "USD",
                merchant_id: transactionData.merchant_id || "default_merchant",
                merchant_category: transactionData.merchant_category || "retail",
                device_fingerprint: transactionData.device_fingerprint || getDeviceFingerprint(),
                ip_address: transactionData.ip_address || "127.0.0.1",
                latitude: transactionData.latitude || 0.0,
                longitude: transactionData.longitude || 0.0,
            };

            try {
                const response = await fetch(`${config.apiUrl}/transactions`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                
                if (!response.ok) {
                    throw new Error(`Oculus API Error: ${response.status}`);
                }
                
                return await response.json();
            } catch (err) {
                console.error("Oculus SDK Error processing transaction:", err);
                throw err;
            }
        }
    };
})();

// Expose globally
window.OculusSDK = OculusSDK;
