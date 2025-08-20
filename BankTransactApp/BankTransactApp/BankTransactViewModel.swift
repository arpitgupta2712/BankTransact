import SwiftUI
import Foundation
import UniformTypeIdentifiers

@MainActor
class BankTransactViewModel: ObservableObject {
    @Published var selectedBank: BankType = .axis
    @Published var selectedFiles: [URL] = []
    @Published var outputFiles: [URL] = []
    @Published var isProcessing = false
    @Published var statusMessage = ""
    @Published var statusColor: Color = .primary
    
    private let fileManager = FileManager.default
    
    func handleFileSelection(_ result: Result<[URL], Error>) {
        switch result {
        case .success(let urls):
            selectedFiles = urls
            statusMessage = "Selected \(urls.count) file(s)"
            statusColor = .blue
        case .failure(let error):
            statusMessage = "Error selecting files: \(error.localizedDescription)"
            statusColor = .red
        }
    }
    
    func processStatements(for bank: BankType) {
        print("DEBUG: processStatements called for \(bank.displayName)")
        isProcessing = true
        statusMessage = "Starting processing..."
        statusColor = .blue
        
        Task {
            do {
                // If files are selected, copy them. Otherwise, use existing files
                if !selectedFiles.isEmpty {
                    try await copyFilesToBankDirectory(for: bank)
                } else {
                    await MainActor.run {
                        statusMessage = "Using existing files in \(bank.displayName) directory..."
                    }
                }
                
                // Run the processing script
                try await runProcessingScript(for: bank)
                
                // Collect output files
                await collectOutputFiles(for: bank)
                
                statusMessage = "Processing completed successfully!"
                statusColor = .green
            } catch {
                statusMessage = "Error: \(error.localizedDescription)"
                statusColor = .red
            }
            
            isProcessing = false
        }
    }
    
    private func copyFilesToBankDirectory(for bank: BankType) async throws {
        let bankDir = getBankDirectory(for: bank)
        let statementsDir = bankDir.appendingPathComponent("data/statements")
        
        await MainActor.run {
            statusMessage = "Copying files to \(bank.displayName) directory..."
        }
        
        // Debug: Print paths
        print("DEBUG: Bank directory: \(bankDir.path)")
        print("DEBUG: Statements directory: \(statementsDir.path)")
        print("DEBUG: Selected files count: \(selectedFiles.count)")
        
        // Create directories if they don't exist
        do {
            try fileManager.createDirectory(at: statementsDir, withIntermediateDirectories: true)
            print("DEBUG: Directory created successfully")
        } catch {
            print("DEBUG: Failed to create directory: \(error)")
            throw BankTransactError.fileCopyFailed
        }
        
        // Copy files
        for (index, file) in selectedFiles.enumerated() {
            let destination = statementsDir.appendingPathComponent(file.lastPathComponent)
            print("DEBUG: Copying file \(index + 1)/\(selectedFiles.count): \(file.lastPathComponent)")
            print("DEBUG: From: \(file.path)")
            print("DEBUG: To: \(destination.path)")
            
            do {
                // Remove existing file if it exists
                if fileManager.fileExists(atPath: destination.path) {
                    try fileManager.removeItem(at: destination)
                    print("DEBUG: Removed existing file")
                }
                try fileManager.copyItem(at: file, to: destination)
                print("DEBUG: File copied successfully")
            } catch {
                print("DEBUG: Failed to copy file: \(error)")
                await MainActor.run {
                    statusMessage = "Failed to copy \(file.lastPathComponent): \(error.localizedDescription)"
                }
                throw BankTransactError.fileCopyFailed
            }
        }
        
        await MainActor.run {
            statusMessage = "Files copied to \(bank.displayName) directory"
        }
    }
    
    private func runProcessingScript(for bank: BankType) async throws {
        let bankDir = getBankDirectory(for: bank)
        let scriptPath: String
        
        switch bank {
        case .axis:
            scriptPath = bankDir.appendingPathComponent("run_complete_workflow.py").path
        case .hdfc:
            scriptPath = bankDir.appendingPathComponent("consolidate_statements.py").path
        }
        
        guard fileManager.fileExists(atPath: scriptPath) else {
            throw BankTransactError.scriptNotFound(bank: bank.displayName)
        }
        
        await MainActor.run {
            statusMessage = "Running \(bank.displayName) processing script..."
        }
        
        print("DEBUG: Starting Python script: \(scriptPath)")
        print("DEBUG: Working directory: \(bankDir.path)")
        
        return try await withCheckedThrowingContinuation { continuation in
            let process = Process()
            
            // Use virtual environment Python for AXIS bank
            let pythonExecutable: String
            if bank == .axis {
                let venvPython = bankDir.appendingPathComponent("axis_env/bin/python").path
                if fileManager.fileExists(atPath: venvPython) {
                    pythonExecutable = venvPython
                    print("DEBUG: Using virtual environment Python: \(pythonExecutable)")
                } else {
                    pythonExecutable = "/usr/bin/python3"
                    print("DEBUG: Virtual environment not found, using system Python")
                }
            } else {
                pythonExecutable = "/usr/bin/python3"
            }
            
            process.executableURL = URL(fileURLWithPath: pythonExecutable)
            process.arguments = [scriptPath]
            process.currentDirectoryURL = bankDir
            
            // Set environment variables for virtual environment
            var env = ProcessInfo.processInfo.environment
            if bank == .axis {
                let venvPath = bankDir.appendingPathComponent("axis_env").path
                env["VIRTUAL_ENV"] = venvPath
                env["PATH"] = "\(venvPath)/bin:" + (env["PATH"] ?? "")
                env["PYTHONPATH"] = venvPath + "/lib/python3.11/site-packages:" + (env["PYTHONPATH"] ?? "")
                print("DEBUG: Set VIRTUAL_ENV to: \(venvPath)")
                print("DEBUG: Set PATH to: \(env["PATH"] ?? "nil")")
                print("DEBUG: Set PYTHONPATH to: \(env["PYTHONPATH"] ?? "nil")")
            }
            process.environment = env
            
            let outputPipe = Pipe()
            let errorPipe = Pipe()
            process.standardOutput = outputPipe
            process.standardError = errorPipe
            
            var hasCompleted = false
            var timeoutTask: Task<Void, Never>?
            
            // Set up real-time output monitoring
            let outputTask = Task {
                let outputHandle = outputPipe.fileHandleForReading
                while let data = try? outputHandle.read(upToCount: 1024), !data.isEmpty {
                    let outputString = String(data: data, encoding: .utf8) ?? ""
                    print("DEBUG: Python output: \(outputString)")
                }
            }
            
            let errorTask = Task {
                let errorHandle = errorPipe.fileHandleForReading
                while let data = try? errorHandle.read(upToCount: 1024), !data.isEmpty {
                    let errorString = String(data: data, encoding: .utf8) ?? ""
                    print("DEBUG: Python error: \(errorString)")
                }
            }
            
            // Set up termination handler
            process.terminationHandler = { process in
                guard !hasCompleted else { return }
                hasCompleted = true
                timeoutTask?.cancel()
                outputTask.cancel()
                errorTask.cancel()
                
                Task { @MainActor in
                    print("DEBUG: Process terminated with status: \(process.terminationStatus)")
                    
                    if process.terminationStatus != 0 {
                        let errorData = errorPipe.fileHandleForReading.readDataToEndOfFile()
                        let errorString = String(data: errorData, encoding: .utf8) ?? "Unknown error"
                        let outputData = outputPipe.fileHandleForReading.readDataToEndOfFile()
                        let outputString = String(data: outputData, encoding: .utf8) ?? ""
                        print("DEBUG: Process error: \(errorString)")
                        print("DEBUG: Process output: \(outputString)")
                        continuation.resume(throwing: BankTransactError.scriptExecutionFailed(error: errorString))
                    } else {
                        let outputData = outputPipe.fileHandleForReading.readDataToEndOfFile()
                        let outputString = String(data: outputData, encoding: .utf8) ?? ""
                        print("DEBUG: Process output: \(outputString)")
                        print("DEBUG: Python script completed successfully")
                        continuation.resume()
                    }
                }
            }
            
            // Set up timeout
            timeoutTask = Task {
                do {
                    try await Task.sleep(nanoseconds: 300_000_000_000) // 5 minutes
                    if !hasCompleted {
                        print("DEBUG: Process timeout - terminating")
                        hasCompleted = true
                        process.terminate()
                        await MainActor.run {
                            continuation.resume(throwing: BankTransactError.scriptExecutionFailed(error: "Script timed out after 5 minutes"))
                        }
                    }
                } catch {
                    // Task was cancelled
                }
            }
            
            // Start the process
            do {
                try process.run()
                print("DEBUG: Process started successfully")
            } catch {
                if !hasCompleted {
                    hasCompleted = true
                    timeoutTask?.cancel()
                    print("DEBUG: Failed to start process: \(error)")
                    continuation.resume(throwing: error)
                }
            }
        }
    }
    
    private func collectOutputFiles(for bank: BankType) async {
        let bankDir = getBankDirectory(for: bank)
        let dataDir = bankDir.appendingPathComponent("data")
        
        var files: [URL] = []
        
        // Collect files from various output directories
        let outputDirs = [
            dataDir.appendingPathComponent("consolidated"),
            dataDir.appendingPathComponent("income"),
            dataDir.appendingPathComponent("income/party"),
            dataDir.appendingPathComponent("expense"),
            dataDir.appendingPathComponent("summary")
        ]
        
        for dir in outputDirs {
            if fileManager.fileExists(atPath: dir.path) {
                do {
                    let contents = try fileManager.contentsOfDirectory(at: dir, includingPropertiesForKeys: nil)
                    files.append(contentsOf: contents.filter { !$0.hasDirectoryPath })
                } catch {
                    print("DEBUG: Error reading directory \(dir.path): \(error)")
                }
            } else {
                print("DEBUG: Directory does not exist: \(dir.path)")
            }
        }
        
        await MainActor.run {
            outputFiles = files
            print("DEBUG: Collected \(files.count) output files")
        }
    }
    
    private func getBankDirectory(for bank: BankType) -> URL {
        let workspaceURL = URL(fileURLWithPath: "/Users/arpitgupta/Downloads/Apps/BankTransact")
        return workspaceURL.appendingPathComponent(bank.rawValue.uppercased())
    }
    
    func checkExistingFiles(for bank: BankType) -> Int {
        let bankDir = getBankDirectory(for: bank)
        let statementsDir = bankDir.appendingPathComponent("data/statements")
        
        do {
            let files = try fileManager.contentsOfDirectory(at: statementsDir, includingPropertiesForKeys: nil)
            return files.filter { $0.pathExtension.lowercased() == "csv" }.count
        } catch {
            return 0
        }
    }
    
    func openFile(_ file: URL) {
        NSWorkspace.shared.open(file)
    }
}

enum BankType: String, CaseIterable {
    case axis = "axis"
    case hdfc = "hdfc"
    
    var displayName: String {
        switch self {
        case .axis: return "AXIS"
        case .hdfc: return "HDFC"
        }
    }
    
    var allowedFileTypes: [UTType] {
        switch self {
        case .axis:
            return [UTType.commaSeparatedText, UTType.plainText]
        case .hdfc:
            return [UTType.spreadsheet, UTType.data]
        }
    }
}

enum BankTransactError: LocalizedError {
    case scriptNotFound(bank: String)
    case scriptExecutionFailed(error: String)
    case fileCopyFailed
    
    var errorDescription: String? {
        switch self {
        case .scriptNotFound(let bank):
            return "Processing script not found for \(bank)"
        case .scriptExecutionFailed(let error):
            return "Script execution failed: \(error)"
        case .fileCopyFailed:
            return "Failed to copy files to processing directory"
        }
    }
}
