import SwiftUI
import Foundation

struct OutputViewer: View {
    let outputFiles: [URL]
    @State private var selectedFile: URL?
    @State private var fileContent: String = ""
    @State private var isLoading = false
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        NavigationView {
            VStack(spacing: 0) {
                // File List
                VStack(alignment: .leading, spacing: 8) {
                    Text("Generated Files")
                        .font(.headline)
                        .padding(.horizontal)
                    
                    List(outputFiles, id: \.self, selection: $selectedFile) { file in
                        HStack {
                            Image(systemName: iconName(for: file))
                                .foregroundColor(iconColor(for: file))
                            
                            VStack(alignment: .leading, spacing: 2) {
                                Text(file.lastPathComponent)
                                    .font(.body)
                                    .lineLimit(1)
                                
                                Text(file.deletingLastPathComponent().lastPathComponent)
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                            }
                            
                            Spacer()
                            
                            Button("Open") {
                                NSWorkspace.shared.open(file)
                            }
                            .buttonStyle(.bordered)
                            .controlSize(.small)
                        }
                        .padding(.vertical, 4)
                    }
                    .listStyle(.plain)
                }
                .frame(width: 300)
                
                Divider()
                
                // File Content Viewer
                VStack(alignment: .leading, spacing: 8) {
                    if let selectedFile = selectedFile {
                        HStack {
                            Text("File: \(selectedFile.lastPathComponent)")
                                .font(.headline)
                            
                            Spacer()
                            
                            if isLoading {
                                ProgressView()
                                    .scaleEffect(0.8)
                            }
                        }
                        .padding(.horizontal)
                        
                        ScrollView {
                            Text(fileContent)
                                .font(.system(.body, design: .monospaced))
                                .padding()
                                .frame(maxWidth: .infinity, alignment: .leading)
                        }
                        .background(Color(.textBackgroundColor))
                        .cornerRadius(8)
                        .padding(.horizontal)
                    } else {
                        VStack {
                            Image(systemName: "doc.text")
                                .font(.system(size: 40))
                                .foregroundColor(.secondary)
                            
                            Text("Select a file to view its content")
                                .font(.headline)
                                .foregroundColor(.secondary)
                        }
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                    }
                }
            }
        }
        .frame(width: 800, height: 600)
        .navigationTitle("Output Files")
        .toolbar {
            ToolbarItem(placement: .primaryAction) {
                Button("Done") {
                    dismiss()
                }
            }
        }
        .onChange(of: selectedFile) { _, file in
            if let file = file {
                loadFileContent(file)
            } else {
                fileContent = ""
            }
        }
    }
    
    private func loadFileContent(_ file: URL) {
        isLoading = true
        
        Task {
            do {
                let content = try String(contentsOf: file, encoding: .utf8)
                await MainActor.run {
                    fileContent = content
                    isLoading = false
                }
            } catch {
                await MainActor.run {
                    fileContent = "Error loading file: \(error.localizedDescription)"
                    isLoading = false
                }
            }
        }
    }
    
    private func iconName(for file: URL) -> String {
        let fileExtension = file.pathExtension.lowercased()
        
        switch fileExtension {
        case "csv":
            return "tablecells"
        case "txt":
            return "doc.text"
        case "xlsx", "xls":
            return "tablecells.badge.ellipsis"
        default:
            return "doc"
        }
    }
    
    private func iconColor(for file: URL) -> Color {
        let fileExtension = file.pathExtension.lowercased()
        
        switch fileExtension {
        case "csv":
            return .green
        case "txt":
            return .blue
        case "xlsx", "xls":
            return .orange
        default:
            return .gray
        }
    }
}

struct OutputViewer_Previews: PreviewProvider {
    static var previews: some View {
        OutputViewer(outputFiles: [])
    }
}
