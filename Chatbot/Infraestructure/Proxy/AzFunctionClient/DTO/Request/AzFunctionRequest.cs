using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace AzFunctionClient.DTO.Request
{
    internal class AzFunctionRequest
    {
        public string question { get; set; }

        public AzFunctionRequest(string question) => this.question = question;
    }
}
