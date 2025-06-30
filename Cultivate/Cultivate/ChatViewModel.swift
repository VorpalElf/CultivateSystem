//
//  ChatViewModel.swift
//  Cultivate
//
//  Created by Jeremy Lo on 25/6/25.
//

import Foundation

class ChatViewModel: ObservableObject {
    @Published var messages: [Message] = [
        Message(text: "Hi, my name is Cultivate. Nice to meet you! How can I help?", isUser: false)
    ]
    @Published var inputText: String = ""
    
    func sendMessage(input: String) {
        messages.append(Message(text: input, isUser: true))
        
        // Generate endpoint URL
        // MARK: Change the address of your server
        guard let url = URL(string: "http://192.168.1.143:5000/server-request") else {
            messages.append(Message(text: "Failed to connect to server", isUser: false))
            return
        }
        
        let history = messages.map { ["text": $0.text, "isUser": $0.isUser] }
        
        // Initiate request
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        let body: [String: Any] = ["input": input, "history": history]
        request.httpBody = try? JSONSerialization.data(withJSONObject: body)
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            guard let data = data,
                  let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
                  let reply = json["response"] as? String else {
                // If error
                DispatchQueue.main.async {
                    self.messages.append(Message(text: "Error", isUser: false))
                }
                return
            }
            DispatchQueue.main.async {
                self.messages.append(Message(text: reply, isUser: false))
            }
        }
        .resume()
    }
    
    func NewConversation() {
        messages = [
                Message(text: "Hi, my name is Cultivate. Nice to meet you! How can I help?", isUser: false)
            ]
    }
}
