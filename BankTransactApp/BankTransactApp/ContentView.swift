import SwiftUI
import UniformTypeIdentifiers

struct ContentView: View {
    @StateObject private var viewModel = BankTransactViewModel()

    @State private var showingFilePicker = false
    @State private var showingOutputViewer = false
    
    var body: some View {
        VStack(spacing: 20) {
            // Header
            VStack(spacing: 8) {
                Image(systemName: "building.2.fill")
                    .font(.system(size: 40))
                    .foregroundColor(.blue)
                
                Text("Bank Transaction Processor")
                    .font(.title)
                    .fontWeight(.bold)
                
                Text("Process and analyze bank statements")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
            }
            .padding(.top, 20)
            
            // Bank Selection
            VStack(alignment: .leading, spacing: 8) {
                Text("Select Bank")
                    .font(.headline)
                
                Picker("Bank", selection: $viewModel.selectedBank) {
                    ForEach(BankType.allCases, id: \.self) { bank in
                        Text(bank.displayName).tag(bank)
                    }
                }
                .pickerStyle(.segmented)
            }
            .padding(.horizontal, 20)
            
            // File Upload Section
            VStack(alignment: .leading, spacing: 12) {
                Text("Upload Statements")
                    .font(.headline)
                
                VStack(spacing: 8) {
                    Button(action: {
                        showingFilePicker = true
                    }) {
                        HStack {
                            Image(systemName: "doc.badge.plus")
                            Text("Select Statement Files")
                        }
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.blue.opacity(0.1))
                        .foregroundColor(.blue)
                        .cornerRadius(8)
                    }
                    .buttonStyle(.plain)
                    
                    if !viewModel.selectedFiles.isEmpty {
                        VStack(alignment: .leading, spacing: 4) {
                            Text("Selected Files (\(viewModel.selectedFiles.count)):")
                                .font(.caption)
                                .foregroundColor(.secondary)
                            
                            ForEach(viewModel.selectedFiles, id: \.self) { file in
                                Text(file.lastPathComponent)
                                    .font(.caption)
                                    .foregroundColor(.primary)
                            }
                        }
                        .padding(.horizontal, 8)
                    }
                    
                    // Show existing files info
                    let existingCount = viewModel.checkExistingFiles(for: viewModel.selectedBank)
                    if existingCount > 0 {
                        VStack(alignment: .leading, spacing: 4) {
                            Text("Existing Files in \(viewModel.selectedBank.displayName) directory (\(existingCount) CSV files):")
                                .font(.caption)
                                .foregroundColor(.secondary)
                            
                            Text("You can process existing files without uploading new ones")
                                .font(.caption)
                                .foregroundColor(.green)
                        }
                        .padding(.horizontal, 8)
                    }
                }
            }
            .padding(.horizontal, 20)
            
            // Process Button
            VStack(spacing: 8) {
                Button(action: {
                    viewModel.processStatements(for: viewModel.selectedBank)
                }) {
                    HStack {
                        if viewModel.isProcessing {
                            ProgressView()
                                .scaleEffect(0.8)
                                .progressViewStyle(CircularProgressViewStyle(tint: .white))
                        } else {
                            Image(systemName: "play.fill")
                        }
                        Text(viewModel.isProcessing ? "Processing..." : "Process Statements")
                    }
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(viewModel.isProcessing ? Color.gray : Color.green)
                    .foregroundColor(.white)
                    .cornerRadius(8)
                }
                .buttonStyle(.plain)
                .disabled(viewModel.isProcessing)
                
                if viewModel.isProcessing {
                    Text("This may take a few minutes...")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            .padding(.horizontal, 20)
            
            // Status and Results
            VStack(spacing: 12) {
                if !viewModel.statusMessage.isEmpty {
                    VStack(alignment: .leading, spacing: 4) {
                        Text("Status:")
                            .font(.headline)
                        
                        Text(viewModel.statusMessage)
                            .font(.body)
                            .foregroundColor(viewModel.statusColor)
                            .padding()
                            .background(viewModel.statusColor.opacity(0.1))
                            .cornerRadius(8)
                    }
                    .padding(.horizontal, 20)
                }
                
                if !viewModel.outputFiles.isEmpty {
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Generated Files:")
                            .font(.headline)
                        
                        ForEach(viewModel.outputFiles, id: \.self) { file in
                            HStack {
                                Image(systemName: "doc.text")
                                    .foregroundColor(.blue)
                                Text(file.lastPathComponent)
                                    .font(.body)
                                Spacer()
                                Button("Open") {
                                    viewModel.openFile(file)
                                }
                                .buttonStyle(.bordered)
                                .controlSize(.small)
                            }
                            .padding(.horizontal, 8)
                        }
                        
                        Button("View All Outputs") {
                            showingOutputViewer = true
                        }
                        .buttonStyle(.bordered)
                        .frame(maxWidth: .infinity)
                    }
                    .padding(.horizontal, 20)
                }
            }
            
            Spacer()
        }
        .frame(minWidth: 600, minHeight: 700)
        .fileImporter(
            isPresented: $showingFilePicker,
            allowedContentTypes: [.commaSeparatedText],
            allowsMultipleSelection: true
        ) { result in
            viewModel.handleFileSelection(result)
        }
        .sheet(isPresented: $showingOutputViewer) {
            OutputViewer(outputFiles: viewModel.outputFiles)
        }
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
