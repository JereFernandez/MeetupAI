using Microsoft.Bot.Builder;
using Microsoft.Bot.Schema;
using Microsoft.Extensions.Logging;
using System.Collections.Generic;
using System.Threading.Tasks;
using System.Threading;
using System;
using Microsoft.Extensions.Configuration;
using AzFunctionClient.InterfaceService;

namespace CoreBot.Bots
{
    public class MainDialog : ActivityHandler
    {
        private readonly ILogger _logger;
        private readonly IConfiguration _configuration;
        private readonly UserState _userState;

        #region proxies
        private readonly IAzFunctionClient _azFunctionClient;
        #endregion


        public MainDialog(ConversationState conversationState, UserState userState, ILogger<MainDialog> logger, IConfiguration configuration, IAzFunctionClient azFunctionClient)
        {
            _logger = logger;
            _configuration = configuration;
            _userState = userState;
            _azFunctionClient = azFunctionClient;
        }

        protected override async Task OnMembersAddedAsync(IList<ChannelAccount> membersAdded, ITurnContext<IConversationUpdateActivity> turnContext, CancellationToken cancellationToken)
        {
            foreach (var member in membersAdded)
            {
                // Greet anyone that was not the target (recipient) of this message.
                // To learn more about Adaptive Cards, see https://aka.ms/msbot-adaptivecards for more details.
                if (member.Id != turnContext.Activity.Recipient.Id)
                {
                    var welcome = MessageFactory.Text("Bienvenido a la meetup! Soy un Chatbot utilizando LangChain para orquestar con OpenAI y SQL.");
                    await turnContext.SendActivityAsync(welcome, cancellationToken);
                }
            }
        }

        protected override async Task<Task> OnMessageActivityAsync(ITurnContext<IMessageActivity> turnContext, CancellationToken cancellationToken)
        {
            _logger.LogInformation("Before proccess activity");

            if (turnContext != null && turnContext.Activity != null)
            {
                await turnContext.SendActivityAsync(new Activity() { Type = ActivityTypes.Typing }, cancellationToken);
                string answer = await _azFunctionClient.SendMessageToOrchestrator(turnContext.Activity.Text);
                await turnContext.SendActivityAsync(MessageFactory.Text(answer), cancellationToken);
            }

            _logger.LogInformation("Activity successful proccess");

            return base.OnMessageActivityAsync(turnContext, cancellationToken);
        }

        public override async Task OnTurnAsync(ITurnContext turnContext, CancellationToken cancellationToken = default(CancellationToken))
        {
            await base.OnTurnAsync(turnContext, cancellationToken);
            await _userState.SaveChangesAsync(turnContext, false, cancellationToken);
        }
    }
}
