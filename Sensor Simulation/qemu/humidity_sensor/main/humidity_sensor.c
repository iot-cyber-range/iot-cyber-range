#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_system.h"
#include "esp_random.h"
#include "mqtt_client.h"
#include "nvs_flash.h"
#include "esp_netif.h"

// MQTT event handler
static esp_err_t mqtt_event_handler_cb(esp_mqtt_event_handle_t event)
{
    esp_mqtt_client_handle_t client = event->client;
    // your_event_handler(event);
    return ESP_OK;
}

static void mqtt_app_start(void)
{

    // Initialize NVS
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
    ESP_ERROR_CHECK(nvs_flash_erase());
    ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);
    // Initialize the default netif
    ESP_ERROR_CHECK(esp_netif_init());
    // Create the default event loop
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    const esp_mqtt_client_config_t mqtt_cfg = {
    .broker.address.uri = "mqtt://172.21.0.2:1883",
    };


    esp_mqtt_client_handle_t client = esp_mqtt_client_init(&mqtt_cfg);
    esp_mqtt_client_register_event(client, ESP_EVENT_ANY_ID, mqtt_event_handler_cb, NULL);
    ESP_ERROR_CHECK(esp_mqtt_client_start(client));

    while (1) {
        // Simulate a humidity sensor by generating a random value between 45% and 55%
        float simulated_humidity = 45 + esp_random() % 11;
        printf("Simulated Humidity: %.2f%%\n", simulated_humidity);

        char msg[50];
        sprintf(msg, "%.2f", simulated_humidity);
        esp_mqtt_client_publish(client, "sensor/humidity", msg, 0, 1, 0);

        // Delay for 10 seconds
        vTaskDelay(10000 / portTICK_PERIOD_MS);
    }
}

void app_main(void)
{
    printf("Humidity Sensor Simulation\n");
    mqtt_app_start();
}


/*
#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_system.h"
#include "esp_random.h"


void app_main(void) {
    printf("Humidity Sensor Simulation\n");

    while (1) {
        // Simulate a humidity sensor by generating a random value between 45% and 55%
        float simulated_humidity = 45 + esp_random() % 11;
        printf("Simulated Humidity: %.2f%%\n", simulated_humidity);

        // Delay for 10 seconds
        vTaskDelay(10000 / portTICK_PERIOD_MS);
    }
}
*/
