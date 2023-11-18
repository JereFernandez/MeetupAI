using AzFunctionClient.InterfaceService;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Net.Http.Json;
using System.Text;
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

        public async Task<string> SendMessageToLLM(string text)
        {
            _logger.LogInformation("Before request to Azure Function");
        
            HttpClient client = CreateConnection();

            var response = await client.PostAsJsonAsync(_configuration.GetValue<string>("AzFunctionEndpoint"), new
            {
                inputText = text
            });

            response.EnsureSuccessStatusCode();

            _logger.LogInformation("Azure Function successfull responsed");

            return await response.Content.ReadAsStringAsync();
        }
    }
}
