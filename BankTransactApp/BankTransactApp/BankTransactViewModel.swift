import SwiftUI
import Foundation
import UniformTypeIdentifiers

// MARK: - Logging Utility
enum LogLevel: String {
    case info = "ℹ️"
    case success = "✅"
    case warning = "⚠️"
    case error = "❌"
    case debug = "🔍"
    case process = "⚙️"
}

struct Logger {
    static func log(_ message: String, level: LogLevel = .info, category: String = "App") {
        let timestamp = DateFormatter.logFormatter.string(from: Date())
        print("[\(timestamp)] \(level.rawValue) [\(category)] \(message)")
    }
    
    static func logProcess(_ message: String) {
        log(message, level: .process, category: "Process")
    }
    
    static func logSuccess(_ message: String) {
        log(message, level: .success, category: "Success")
    }
    
    static func logError(_ message: String) {
        log(message, level: .error, category: "Error")
    }
    
    static func logDebug(_ message: String) {
        log(message, level: .debug, category: "Debug")
    }
}

extension DateFormatter {
    static let logFormatter: DateFormatter = {
        let formatter = DateFormatter()
        formatter.dateFormat = "HH:mm:ss"
        return formatter
    }()
}

// MARK: - Error Types
enum BankTransactError: Error, LocalizedError {
    case scriptNotFound(bank: String)
    case scriptExecutionFailed(error: String)
    case fileCopyFailed(error: String)
    case noFilesSelected
    
    var errorDescription: String? {
        switch self {
        case .scriptNotFound(let bank):
            return "Processing script not found for \(bank)"
        case .scriptExecutionFailed(let error):
            return "Script execution failed: \(error)"
        case .fileCopyFailed(let error):
            return "Failed to copy files: \(error)"
        case .noFilesSelected:
            return "No files selected for processing"
        }
    }
}

// MARK: - Bank Types
enum BankType: String, CaseIterable {
    case axis = "AXIS"
    case hdfc = "HDFC"
    
    var displayName: String {
        return self.rawValue
    }
    
    var allowedFileTypes: [UTType] {
        return [.commaSeparatedText]
    }
}

// MARK: - View Model
@MainActor
class BankTransactViewModel: ObservableObject {
    @Published var selectedBank: BankType = .axis
    @Published var selectedFiles: [URL] = []
    @Published var outputFiles: [URL] = []
    @Published var isProcessing = false
    @Published var statusMessage = ""
    @Published var statusColor: Color = .primary
    
    private let fileManager = FileManager.default
    
    // MARK: - File Selection
    func selectFiles() {
        Logger.log("File selection initiated")
        // File selection logic handled by ContentView
    }
    
    func addSelectedFiles(_ urls: [URL]) {
        Logger.log("Adding \(urls.count) selected files")
        selectedFiles.append(contentsOf: urls)
        Logger.logSuccess("Files added successfully")
    }
    
    // MARK: - File Management
    private func getBankDirectory(for bank: BankType) -> URL {
        // Use the current user's project directory path
        let homeDirectory = fileManager.homeDirectoryForCurrentUser
        let projectPath = homeDirectory.appendingPathComponent("Downloads/Apps/BankTransact")
        return projectPath.appendingPathComponent(bank.displayName)
    }
    
    private func copyFilesToBankDirectory() throws {
        Logger.log("Starting file copy process")
        
        guard !selectedFiles.isEmpty else {
            Logger.logError("No files selected for copying")
            throw BankTransactError.noFilesSelected
        }
        
        let bankDir = getBankDirectory(for: selectedBank)
        let statementsDir = bankDir.appendingPathComponent("data/statements")
        
        // Check if we can access the bank directory
        guard fileManager.isWritableFile(atPath: bankDir.path) else {
            Logger.logError("No write permission for bank directory: \(bankDir.path)")
            throw BankTransactError.fileCopyFailed(error: "No write permission for bank directory. Please check folder permissions.")
        }
        
        // Create directory if it doesn't exist
        do {
            try fileManager.createDirectory(at: statementsDir, withIntermediateDirectories: true)
            Logger.logProcess("Created directory: \(statementsDir.path)")
        } catch {
            Logger.logError("Failed to create directory: \(error.localizedDescription)")
            throw BankTransactError.fileCopyFailed(error: "Failed to create statements directory: \(error.localizedDescription)")
        }
        
        var copiedCount = 0
        for fileURL in selectedFiles {
            let fileName = fileURL.lastPathComponent
            let destinationURL = statementsDir.appendingPathComponent(fileName)
            
            do {
                if fileManager.fileExists(atPath: destinationURL.path) {
                    try fileManager.removeItem(at: destinationURL)
                    Logger.logProcess("Removed existing file: \(fileName)")
                }
                try fileManager.copyItem(at: fileURL, to: destinationURL)
                copiedCount += 1
                Logger.logProcess("Copied: \(fileName)")
            } catch {
                Logger.logError("Failed to copy \(fileName): \(error.localizedDescription)")
                throw BankTransactError.fileCopyFailed(error: "Failed to copy \(fileName): \(error.localizedDescription)")
            }
        }
        
        Logger.logSuccess("Successfully copied \(copiedCount) files to \(selectedBank.displayName) directory")
    }
    
    func checkExistingFiles(for bank: BankType) -> Int {
        let bankDir = getBankDirectory(for: bank)
        let statementsDir = bankDir.appendingPathComponent("data/statements")
        
        do {
            let files = try fileManager.contentsOfDirectory(at: statementsDir, includingPropertiesForKeys: nil)
            return files.filter { $0.pathExtension.lowercased() == "csv" }.count
        } catch {
            Logger.logDebug("No existing files found in \(bank.displayName) directory")
            return 0
        }
    }
    
    // MARK: - Processing
    func processStatements(for bank: BankType) {
        Logger.log("Starting processing for \(bank.displayName)")
        isProcessing = true
        statusMessage = "Starting processing..."
        statusColor = .blue
        
        Task {
            do {
                // Copy files if any are selected
                if !selectedFiles.isEmpty {
                    try copyFilesToBankDirectory()
                }
                
                // Run the processing script
                try await runProcessingScript(for: bank)
                
                // Collect output files
                await collectOutputFiles(for: bank)
                
                await MainActor.run {
                    statusMessage = "Processing completed successfully!"
                    statusColor = .green
                    isProcessing = false
                    Logger.logSuccess("Processing completed for \(bank.displayName)")
                }
                
            } catch {
                await MainActor.run {
                    statusMessage = "Error: \(error.localizedDescription)"
                    statusColor = .red
                    isProcessing = false
                    Logger.logError("Processing failed: \(error.localizedDescription)")
                }
            }
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
            Logger.logError("Script not found: \(scriptPath)")
            throw BankTransactError.scriptNotFound(bank: bank.displayName)
        }
        
        Logger.logProcess("Executing script: \(scriptPath)")
        
        return try await withCheckedThrowingContinuation { continuation in
            let process = Process()
            
            // Use virtual environment Python for AXIS bank
            let pythonExecutable: String
            if bank == .axis {
                let venvPython = bankDir.appendingPathComponent("axis_env/bin/python").path
                if fileManager.fileExists(atPath: venvPython) {
                    pythonExecutable = venvPython
                    Logger.logDebug("Using virtual environment Python")
                } else {
                    pythonExecutable = "/usr/bin/python3"
                    Logger.logDebug("Using system Python")
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
                Logger.logDebug("Virtual environment configured")
            }
            process.environment = env
            
            let outputPipe = Pipe()
            let errorPipe = Pipe()
            process.standardOutput = outputPipe
            process.standardError = errorPipe
            
            var hasCompleted = false
            var timeoutTask: Task<Void, Never>?
            var outputBuffer = ""
            var errorBuffer = ""
            
            // Set up real-time output monitoring with filtering
            let outputTask = Task {
                let outputHandle = outputPipe.fileHandleForReading
                while let data = try? outputHandle.read(upToCount: 1024), !data.isEmpty {
                    let outputString = String(data: data, encoding: .utf8) ?? ""
                    outputBuffer += outputString
                    
                    // Only log important messages, skip verbose debug output
                    let lines = outputString.components(separatedBy: .newlines)
                    for line in lines {
                        let trimmed = line.trimmingCharacters(in: .whitespaces)
                        if !trimmed.isEmpty && shouldLogOutputLine(trimmed) {
                            Logger.logProcess(trimmed)
                        }
                    }
                }
            }
            
            let errorTask = Task {
                let errorHandle = errorPipe.fileHandleForReading
                while let data = try? errorHandle.read(upToCount: 1024), !data.isEmpty {
                    let errorString = String(data: data, encoding: .utf8) ?? ""
                    errorBuffer += errorString
                    
                    // Log all error messages
                    let lines = errorString.components(separatedBy: .newlines)
                    for line in lines {
                        let trimmed = line.trimmingCharacters(in: .whitespaces)
                        if !trimmed.isEmpty {
                            Logger.logError(trimmed)
                        }
                    }
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
                    Logger.logProcess("Process terminated with status: \(process.terminationStatus)")
                    
                    if process.terminationStatus != 0 {
                        Logger.logError("Script execution failed")
                        continuation.resume(throwing: BankTransactError.scriptExecutionFailed(error: errorBuffer.isEmpty ? "Unknown error" : errorBuffer))
                    } else {
                        Logger.logSuccess("Script completed successfully")
                        continuation.resume()
                    }
                }
            }
            
            // Set up timeout
            timeoutTask = Task {
                do {
                    try await Task.sleep(nanoseconds: 300_000_000_000) // 5 minutes
                    if !hasCompleted {
                        Logger.logError("Process timeout - terminating")
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
                Logger.logProcess("Process started successfully")
            } catch {
                if !hasCompleted {
                    hasCompleted = true
                    timeoutTask?.cancel()
                    Logger.logError("Failed to start process: \(error.localizedDescription)")
                    continuation.resume(throwing: error)
                }
            }
        }
    }
    
    // MARK: - Output Filtering
    private func shouldLogOutputLine(_ line: String) -> Bool {
        // Skip verbose debug output
        let skipPatterns = [
            "DEBUG: Python output:",
            "Skipping duplicate transaction:",
            "Processing:",
            "Extracted",
            "Added",
            "Found opening balance:",
            "Found closing balance:",
            "Sample data"
        ]
        
        for pattern in skipPatterns {
            if line.contains(pattern) {
                return false
            }
        }
        
        // Only log important messages
        let importantPatterns = [
            "✅",
            "❌",
            "📊",
            "📁",
            "📋",
            "🎉",
            "Step",
            "completed",
            "successfully",
            "error",
            "failed",
            "Copied:",
            "Generated",
            "Workflow"
        ]
        
        for pattern in importantPatterns {
            if line.contains(pattern) {
                return true
            }
        }
        
        return false
    }
    
    // MARK: - Output Collection
    private func collectOutputFiles(for bank: BankType) async {
        Logger.log("Collecting output files")
        
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
            do {
                let dirFiles = try fileManager.contentsOfDirectory(at: dir, includingPropertiesForKeys: nil)
                files.append(contentsOf: dirFiles)
            } catch {
                Logger.logDebug("No files found in \(dir.lastPathComponent)")
            }
        }
        
        await MainActor.run {
            self.outputFiles = files.sorted { $0.lastPathComponent < $1.lastPathComponent }
            Logger.logSuccess("Collected \(files.count) output files")
        }
    }
    
    // MARK: - File Operations
    func openFile(_ url: URL) {
        Logger.log("Opening file: \(url.lastPathComponent)")
        NSWorkspace.shared.open(url)
    }
    
    func openAllOutputs() {
        Logger.log("Opening all output files")
        for file in outputFiles {
            NSWorkspace.shared.open(file)
        }
    }
}

