// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.
//
// Generated with Bot Builder V4 SDK Template for Visual Studio CoreBot v4.18.1

using Microsoft.Bot.Builder;
using Microsoft.Bot.Builder.Integration.AspNet.Core;
using Microsoft.Bot.Builder.TraceExtensions;
using Microsoft.Bot.Connector.Authentication;
using Microsoft.Bot.Schema;
using Microsoft.Extensions.Logging;
using System;

namespace CoreBot
{
    public class AdapterWithErrorHandler : CloudAdapter
    {
        public AdapterWithErrorHandler(BotFrameworkAuthentication auth, ILogger<IBotFrameworkHttpAdapter> logger, ConversationState conversationState = default)
            : base(auth, logger)
        {
            OnTurnError = async (turnContext, ex) =>
            {
                string codeError = Guid.NewGuid().ToString();
                // Log any leaked exception from the application.
                logger.LogError("Code Error: {codeError} - Error: {description} - InnerException: {InnerException} - StackTrace: {StackTrace}", codeError, ex.Message, ex.InnerException, ex.StackTrace);

                await turnContext.SendActivityAsync(MessageFactory.Text($"Se produjo un error de gravedad con el código {codeError}"));

                if (conversationState != null)
                {
                    try
                    {
                        await conversationState.DeleteAsync(turnContext);
                    }
                    catch (Exception e)
                    {
                        logger.LogError(e, $"Exception caught on attempting to Delete ConversationState : {e.Message}");
                    }
                }

                // Send a trace activity, which will be displayed in the Bot Framework Emulator
                await turnContext.TraceActivityAsync("OnTurnError Trace", ex.Message, "https://www.botframework.com/schemas/error", "TurnError");
            };
        }
    }
}
