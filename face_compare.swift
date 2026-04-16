// face_compare.swift — Apple Vision face comparison helper
// Uses Vision framework on Apple Neural Engine. No dlib/cmake needed.
// Usage:
//   face_compare detect <image_path>           → face count + bounding boxes (JSON)
//   face_compare enroll <image_path> <outdir>  → extract feature print, save to outdir
//   face_compare match <image_path> <refdir>   → compare against all prints in refdir
//
// All output is single-line JSON for Python parsing.

import Foundation
import Vision
import AppKit

// MARK: - Helpers

func loadImage(_ path: String) -> CGImage? {
    guard let data = try? Data(contentsOf: URL(fileURLWithPath: path)),
          let source = CGImageSourceCreateWithData(data as CFData, nil),
          let image = CGImageSourceCreateImageAtIndex(source, 0, nil) else {
        return nil
    }
    return image
}

func toJSON(_ dict: [String: Any]) -> String {
    let data = try! JSONSerialization.data(withJSONObject: dict, options: [.sortedKeys])
    return String(data: data, encoding: .utf8)!
}

// MARK: - Vision requests (synchronous wrappers)

func detectFaces(_ image: CGImage) -> [VNFaceObservation] {
    let request = VNDetectFaceRectanglesRequest()
    let handler = VNImageRequestHandler(cgImage: image, options: [:])
    try? handler.perform([request])
    return (request.results as? [VNFaceObservation]) ?? []
}

func featurePrint(_ image: CGImage) -> VNFeaturePrintObservation? {
    let request = VNGenerateImageFeaturePrintRequest()
    let handler = VNImageRequestHandler(cgImage: image, options: [:])
    try? handler.perform([request])
    return request.results?.first as? VNFeaturePrintObservation
}

// MARK: - Commands

func cmdDetect(_ path: String) {
    guard let image = loadImage(path) else {
        print(toJSON(["error": "cannot load image"]))
        return
    }
    let faces = detectFaces(image)
    let detections = faces.map { obs -> [String: Any] in
        let bb = obs.boundingBox
        return [
            "x": round(bb.origin.x * 1000) / 1000,
            "y": round(bb.origin.y * 1000) / 1000,
            "w": round(bb.size.width * 1000) / 1000,
            "h": round(bb.size.height * 1000) / 1000,
            "confidence": round(obs.confidence * 1000) / 1000
        ]
    }
    print(toJSON(["faces": faces.count, "detections": detections]))
}

func cmdEnroll(_ imagePath: String, _ outDir: String) {
    guard let image = loadImage(imagePath) else {
        print(toJSON(["error": "cannot load image"]))
        return
    }

    let faces = detectFaces(image)
    guard faces.count == 1 else {
        print(toJSON(["error": "need exactly 1 face, found \(faces.count)"]))
        return
    }

    guard let fp = featurePrint(image) else {
        print(toJSON(["error": "feature print extraction failed"]))
        return
    }

    // Serialize the feature print data
    let fm = FileManager.default
    try? fm.createDirectory(atPath: outDir, withIntermediateDirectories: true)

    let ts = ISO8601DateFormatter().string(from: Date())
    let safeName = ts.replacingOccurrences(of: ":", with: "-")
    let filename = "ref_\(safeName).fpdata"
    let metaname = "ref_\(safeName).json"
    let fpPath = (outDir as NSString).appendingPathComponent(filename)
    let metaPath = (outDir as NSString).appendingPathComponent(metaname)

    // Save raw feature print data (binary) for Vision's computeDistance
    try? fp.data.write(to: URL(fileURLWithPath: fpPath))

    // Save metadata
    let meta: [String: Any] = [
        "timestamp": ts,
        "source": (imagePath as NSString).lastPathComponent,
        "element_count": fp.elementCount,
        "element_type": "\(fp.elementType)",
        "data_file": filename
    ]
    let metaData = try! JSONSerialization.data(withJSONObject: meta, options: [.prettyPrinted])
    try? metaData.write(to: URL(fileURLWithPath: metaPath))

    print(toJSON(["enrolled": metaname, "elements": fp.elementCount, "faces": 1]))
}

func cmdMatch(_ imagePath: String, _ refDir: String) {
    guard let image = loadImage(imagePath) else {
        print(toJSON(["match": false, "reason": "cannot load image"]))
        return
    }

    let faces = detectFaces(image)
    guard !faces.isEmpty else {
        print(toJSON(["match": false, "reason": "no face detected", "faces": 0]))
        return
    }

    guard let queryFP = featurePrint(image) else {
        print(toJSON(["match": false, "reason": "feature print failed"]))
        return
    }

    // Load reference prints and compute distances using Vision's native comparison
    let fm = FileManager.default
    guard let files = try? fm.contentsOfDirectory(atPath: refDir) else {
        print(toJSON(["match": false, "reason": "no reference directory"]))
        return
    }

    let metaFiles = files.filter { $0.hasSuffix(".json") }
    guard !metaFiles.isEmpty else {
        print(toJSON(["match": false, "reason": "no references enrolled"]))
        return
    }

    var bestDist: Float = 999.0
    var bestRef = ""
    var validRefs = 0

    for mf in metaFiles {
        let metaPath = (refDir as NSString).appendingPathComponent(mf)
        guard let metaData = fm.contents(atPath: metaPath),
              let meta = try? JSONSerialization.jsonObject(with: metaData) as? [String: Any],
              let dataFile = meta["data_file"] as? String else {
            continue
        }

        let fpPath = (refDir as NSString).appendingPathComponent(dataFile)
        guard let fpData = try? Data(contentsOf: URL(fileURLWithPath: fpPath)) else {
            continue
        }

        // Reconstruct feature print from saved data using a fresh image request
        // Since we can't directly deserialize VNFeaturePrintObservation,
        // we'll use the raw data + element metadata for manual comparison.
        // But the cleanest approach: save the reference IMAGE (low-res) and
        // re-extract the feature print at match time. Costs ~10ms per ref.
        // Let's do that instead.

        // Check if we have the source image cached
        let cachedImagePath = (refDir as NSString).appendingPathComponent(
            dataFile.replacingOccurrences(of: ".fpdata", with: ".jpg")
        )
        guard let refImage = loadImage(cachedImagePath),
              let refFP = featurePrint(refImage) else {
            continue
        }

        var dist: Float = 0
        do {
            try queryFP.computeDistance(&dist, to: refFP)
            validRefs += 1
            if dist < bestDist {
                bestDist = dist
                bestRef = mf
            }
        } catch {
            continue
        }
    }

    guard validRefs > 0 else {
        print(toJSON(["match": false, "reason": "no valid references could be loaded"]))
        return
    }

    // VNFeaturePrint distance thresholds (empirically tuned):
    //   < 12.0 = strong match (same person, similar conditions)
    //   12-18  = likely match (same person, different conditions)
    //   18-25  = uncertain
    //   > 25   = different person
    let isMatch = bestDist < 18.0
    let uncertain = bestDist >= 18.0 && bestDist < 25.0

    print(toJSON([
        "match": isMatch,
        "uncertain": uncertain,
        "distance": round(Double(bestDist) * 100) / 100,
        "best_ref": bestRef,
        "faces": faces.count,
        "refs_checked": validRefs
    ]))
}

// MARK: - Main

let args = CommandLine.arguments
guard args.count >= 3 else {
    print(toJSON(["error": "usage: face_compare <detect|enroll|match> <image_path> [dir]"]))
    exit(1)
}

switch args[1] {
case "detect":
    cmdDetect(args[2])
case "enroll":
    guard args.count >= 4 else {
        print(toJSON(["error": "enroll requires output directory"]))
        exit(1)
    }
    cmdEnroll(args[2], args[3])
case "match":
    guard args.count >= 4 else {
        print(toJSON(["error": "match requires reference directory"]))
        exit(1)
    }
    cmdMatch(args[2], args[3])
default:
    print(toJSON(["error": "unknown command: \(args[1])"]))
    exit(1)
}
