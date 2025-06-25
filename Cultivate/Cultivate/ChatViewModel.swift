//
//  ChatViewModel.swift
//  Cultivate
//
//  Created by Jeremy Lo on 25/6/25.
//

import Foundation

class ChatViewModel: ObservableObject {
    @Published var messages: [Message] = [
        Message(text: "Nice, what's your name", isUser: true),
        Message(text: "Hello, how can I help?", isUser: false),
        Message(text: "Hi, my name is Gemini. Nice to meet you! How can I help?", isUser: false)
    ]
    @Published var inputText: String = ""
    
    func sendMessage(input: String) {
        messages.append(Message(text: input, isUser: true))
        var ans: String = ""
        
        messages.append(Message(text: "Done", isUser: false))
    }
}
