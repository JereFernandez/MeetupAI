using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace AzFunctionClient.InterfaceService
{
    public interface IAzFunctionClient
    {
        Task<string> SendMessageToOrchestrator(string inputText);
    }
}
