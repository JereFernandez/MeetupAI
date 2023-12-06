using AzFunctionClient.DTO.Request;
using AzFunctionClient.InterfaceService;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Net.Http.Json;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;

namespace AzFunctionClient.Service
{
    public class AzFunctionClientService : IAzFunctionClient
    {
        private readonly IHttpClientFactory _httpClientFactory;
        private readonly ILogger<AzFunctionClientService> _logger;
        private readonly IConfiguration _configuration;

        public AzFunctionClientService(IHttpClientFactory httpClientFactory,
            ILogger<AzFunctionClientService> logger,
            IConfiguration configuration) => (_httpClientFactory, _logger, _configuration) = (httpClientFactory, logger, configuration);

        private HttpClient CreateConnection() => _httpClientFactory.CreateClient(nameof(AzFunctionClientService));

        public async Task<string> SendMessageToOrchestrator(string inputText)
        {
            _logger.LogInformation("Before request to Azure Function");

            HttpClient client = CreateConnection();

            using StringContent json = new(JsonSerializer.Serialize
                (new
                    {
                        question = inputText
                    }
                )
                , Encoding.UTF8
                , "application/json");

            var response = await client.PostAsync(_configuration.GetValue<string>("AzFunctionEndpoint"), json);
            response.EnsureSuccessStatusCode();

            _logger.LogInformation("Azure Function successfull responsed");

            return await response.Content.ReadAsStringAsync();
        }
    }
}
