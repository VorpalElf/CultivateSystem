//
//  ContentView.swift
//  Cultivate
//
//  Created by Jeremy Lo on 25/6/25.
//

import SwiftUI
import MarkdownUI

struct Message: Identifiable {
    let id = UUID()
    let text: String
    let isUser: Bool
}

struct ContentView: View {
    @ObservedObject private var viewModel = ChatViewModel()
    @State private var inputString: String = ""
    @FocusState private var isFocused: Bool
    
    var body: some View {
        NavigationView {
            VStack {
                Divider()
                    .frame(minHeight: 15)
                
                // Chat History View
                ScrollView {
                    VStack(alignment: .leading, spacing: 8) {
                        ForEach(viewModel.messages) { message in
                            HStack {
                                if message.isUser {
                                    Spacer()
                                    Text(message.text)
                                        .padding(.horizontal, 16)
                                        .padding(.vertical, 10)
                                        .background(Color.blue)
                                        .foregroundColor(.white)
                                        .cornerRadius(10)
                                        .frame(maxWidth: 280, alignment: .trailing)
                                } else {
                                    Markdown(message.text)
                                        .padding(.horizontal, 16)
                                        .padding(.vertical, 10)
                                        .background(Color.gray.opacity(0.2))
                                        .foregroundColor(.black)
                                        .cornerRadius(10)
                                        .frame(maxWidth: 300, alignment: .leading)
                                    Spacer()
                                }
                            }
                            .frame(maxWidth: .infinity)
                        }
                    }
                    .padding()
                }
                .onTapGesture {
                    isFocused = false
                }
                
                Divider()
                // Input View
                HStack {
                    TextField("Type here...", text: $inputString)
                        .padding(10)
                        .background(Color(.systemGray6))
                        .cornerRadius(10)
                        .focused($isFocused)
                    
                    Button("Send") {
                        viewModel.sendMessage(input: inputString)
                        inputString = ""
                    }
                    .padding(8)
                }
                .padding()
            }
            .toolbar {
                Button {
                    viewModel.NewConversation()
                } label: {
                    Image(systemName: "square.and.pencil")
                        .foregroundColor(.blue)
                }
            }
        }
    }
}
#Preview {
    ContentView()
}
