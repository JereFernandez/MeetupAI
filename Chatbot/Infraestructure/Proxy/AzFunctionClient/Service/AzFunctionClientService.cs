using AzFunctionClient.InterfaceService;
using Microsoft.Extensions.Logging;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace AzFunctionClient.Service
{
    public class AzFunctionClientService : IAzFunctionClient, IDisposable
    {
        private readonly HttpClient _httpClient;
        private readonly ILogger<AzFunctionClientService> _logger;

        public AzFunctionClientService(HttpClient httpClient, ILogger<AzFunctionClientService> logger) => (_httpClient, _logger) = (httpClient, logger);

        public void Dispose() => _httpClient?.Dispose();

        public async Task<string> SendMessageToLLM(string text)
        {

            return "";
        }
    }
}
