/**
 * WebSocket Client for Lambda Visualizer
 * Gestisce la comunicazione real-time con il backend
 */

class LambdaVisualizerWebSocketClient {
    constructor(uri = 'ws://localhost:8765') {
        this.uri = uri;
        this.websocket = null;
        this.clientId = null;
        this.messageHandlers = new Map();
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000; // 1 second
    }

    connect() {
        return new Promise((resolve, reject) => {
            try {
                this.websocket = new WebSocket(this.uri);
                
                this.websocket.onopen = (event) => {
                    console.log('🔗 Connected to Lambda Visualizer WebSocket');
                    this.reconnectAttempts = 0;
                    resolve(event);
                };

                this.websocket.onmessage = (event) => {
                    this.handleMessage(event);
                };

                this.websocket.onclose = (event) => {
                    console.log('🔌 WebSocket connection closed');
                    this.handleReconnect();
                };

                this.websocket.onerror = (error) => {
                    console.error('❌ WebSocket error:', error);
                    reject(error);
                };

            } catch (error) {
                console.error('❌ Failed to create WebSocket connection:', error);
                reject(error);
            }
        });
    }

    handleMessage(event) {
        try {
            const data = JSON.parse(event.data);
            
            // Store client ID if provided
            if (data.type === 'system_update' && data.data.client_id) {
                this.clientId = data.data.client_id;
                console.log('📋 Assigned client ID:', this.clientId);
            }

            // Call registered handlers
            if (this.messageHandlers.has(data.type)) {
                this.messageHandlers.get(data.type)(data.data);
            } else {
                console.log('📨 Received message:', data.type, data.data);
            }

        } catch (error) {
            console.error('❌ Error parsing WebSocket message:', error);
        }
    }

    handleReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`🔄 Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
            
            setTimeout(() => {
                this.connect().catch(error => {
                    console.error('❌ Reconnection failed:', error);
                });
            }, this.reconnectDelay * this.reconnectAttempts);
        } else {
            console.error('❌ Max reconnection attempts reached');
        }
    }

    sendMessage(type, data) {
        if (!this.websocket || this.websocket.readyState !== WebSocket.OPEN) {
            console.error('❌ WebSocket not connected');
            return;
        }

        const message = {
            type: type,
            data: data,
            message_id: this.generateMessageId()
        };

        this.websocket.send(JSON.stringify(message));
        console.log('📤 Sent message:', type);
    }

    onMessage(type, handler) {
        this.messageHandlers.set(type, handler);
    }

    submitJob(expression, config = {}) {
        this.sendMessage('job_submit', {
            job_type: 'lambda_analysis',
            input_data: {
                expression: expression,
                config: config,
                strategy: 'normal_order'
            }
        });
    }

    subscribeToJobs() {
        this.sendMessage('subscribe', {
            subscription_type: 'my_jobs'
        });
    }

    ping() {
        this.sendMessage('ping', {});
    }

    disconnect() {
        if (this.websocket) {
            this.websocket.close();
            this.websocket = null;
        }
    }

    generateMessageId() {
        return Math.random().toString(36).substr(2, 9);
    }
}

// Export for use in other modules
export default LambdaVisualizerWebSocketClient;
